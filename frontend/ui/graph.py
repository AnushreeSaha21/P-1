import streamlit as st
import networkx as nx
import pandas as pd
import tempfile
from streamlit.components.v1 import html

from backend.graph.graph_service import (
    load_graph,
    search_pan,
    load_subgraph,
    get_dashboard,
    find_bridge_pans
)


def show_graph():

    st.title("🕸️ PAN Relationship Graph")

    st.write(
        "Visualize relationships between PANs based on FIU transactions."
    )

    st.divider()

    graph = load_graph()

    st.success("Graph built successfully!")

    if "graph_pan" not in st.session_state:
        st.session_state.graph_pan = None

    if "graph_result" not in st.session_state:
        st.session_state.graph_result = None

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Nodes",
        graph.number_of_nodes()
    )

    col2.metric(
        "Edges",
        graph.number_of_edges()
    )

    col3.metric(
        "Connected Components",
        nx.number_weakly_connected_components(graph)
    )


    st.subheader("🔥 Top Connected PANs")

    dashboard = get_dashboard(graph)

    dashboard_df = pd.DataFrame(dashboard)

    st.dataframe(
        dashboard_df,
        use_container_width=True,
        hide_index=True
    )

    bridge_pans = find_bridge_pans(graph, limit=15)

    bridge_df = pd.DataFrame(bridge_pans)

    st.subheader("🌉 Top 15 Bridge PANs")

    st.dataframe(
        bridge_df,
        use_container_width=True,
        hide_index=True
)

    st.subheader("🔍 Explore PAN")

    manual_pan = st.text_input(
        "Enter PAN",
        placeholder="e.g. ABCDE1234F"
    )

    st.subheader("🌐 Network Visualization")

    # =========================================================
    # VISUALIZE PAN
    # =========================================================

    if st.button("🔎 Visualize"):

        pan = manual_pan.strip().upper()

        if not pan:

            st.warning("Please enter a PAN.")

        else:

            result = search_pan(graph, pan)

            if result is None:

                st.error("PAN not found.")

            elif result["degree"] == 0:

                st.info("This PAN has no connected PANs.")

            else:

                # Save selected PAN and result
                st.session_state.graph_pan = pan
                st.session_state.graph_result = result


    # =========================================================
    # GET CURRENT SELECTED PAN
    # =========================================================

    pan = st.session_state.graph_pan
    result = st.session_state.graph_result


    # =========================================================
    # DISPLAY PAN DETAILS
    # =========================================================

    if pan and result:

        st.subheader(
            result["name"] or "Unknown Name"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Connections",
            result["degree"]
        )

        c2.metric(
            "Incoming",
            result["flow"]["incoming"]
        )

        c3.metric(
            "Outgoing",
            result["flow"]["outgoing"]
        )


        # =====================================================
        # DIRECTLY CONNECTED PANS
        # =====================================================

        st.markdown(
            "### Directly Connected PANs"
        )

        neighbors_df = pd.DataFrame(
            result["neighbors"],
            columns=["Connected PAN"]
        )

        st.dataframe(
            neighbors_df,
            use_container_width=True
        )


        st.markdown(
            f"Connected Component: "
            f"{len(result['component'])} PANs"
        )


        # =====================================================
        # NETWORK VISUALIZATION
        # =====================================================

        st.subheader("🌐 Network Visualization")

        network = load_subgraph(
            graph,
            pan
        )

        if network is not None:

            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".html"
            )

            network.save_graph(tmp.name)

            with open(
                tmp.name,
                "r",
                encoding="utf-8"
            ) as f:

                html_content = f.read()

            # =====================================================
            # ADD ZOOM CONTROLS
            # =====================================================

            zoom_controls = """
            <div id="zoom-controls"
                style="
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    z-index: 9999;
                    display: flex;
                    gap: 6px;
                ">

                <button
                    onclick="zoomIn()"
                    style="
                        width: 42px;
                        height: 38px;
                        font-size: 22px;
                        font-weight: bold;
                        cursor: pointer;
                        border-radius: 6px;
                        border: 1px solid #555;
                        background: #262730;
                        color: white;
                    ">
                    +
                </button>

                <button
                    onclick="zoomOut()"
                    style="
                        width: 42px;
                        height: 38px;
                        font-size: 22px;
                        font-weight: bold;
                        cursor: pointer;
                        border-radius: 6px;
                        border: 1px solid #555;
                        background: #262730;
                        color: white;
                    ">
                    −
                </button>

                <button
                    onclick="resetZoom()"
                    style="
                        width: 65px;
                        height: 38px;
                        font-size: 14px;
                        cursor: pointer;
                        border-radius: 6px;
                        border: 1px solid #555;
                        background: #262730;
                        color: white;
                    ">
                    Reset
                </button>

            </div>

            <script>

                function zoomIn() {

                    if (typeof network !== "undefined") {

                        var scale =
                            network.getScale();

                        network.moveTo({
                            scale: scale * 1.2
                        });

                    }

                }


                function zoomOut() {

                    if (typeof network !== "undefined") {

                        var scale =
                            network.getScale();

                        network.moveTo({
                            scale: scale / 1.2
                        });

                    }

                }


                function resetZoom() {

                    if (typeof network !== "undefined") {

                        network.fit({
                            animation: true
                        });

                    }

                }

            </script>
            """


            # Insert controls after <body>
            html_content = html_content.replace(
                "<body>",
                "<body>" + zoom_controls
            )


        # =====================================================
        # EXISTING STYLING
        # =====================================================



            html_content = html_content.replace(
                "</head>",
                """
                <style>

                    html, body {
                        margin: 0 !important;
                        padding: 0 !important;
                        background: #0E1117 !important;
                        overflow: hidden;
                    }

                    #mynetwork {
                        border: none !important;
                    }

                    canvas {
                        border: none !important;
                    }

                </style>
                </head>
                """
            )


            html(
                html_content,
                height=750,
                scrolling=False
            )


        # =====================================================
        # AI ANALYSIS
        # =====================================================

        st.divider()

        st.subheader("🤖 AI Network Insights")

        if st.button("🔎 Analyze PAN Network"):

            graph_context = {

                "pan": pan,

                "name": result["name"],

                "connections": result["degree"],

                "incoming": result["flow"]["incoming"],

                "outgoing": result["flow"]["outgoing"],

                "direct_connections": result["neighbors"],

                "connected_component_size": len(
                    result["component"]
                )
            }


            with st.spinner(
                "Analyzing PAN network..."
            ):

                from backend.ai.ollama_service import (
                    analyze_graph
                )

                ai_result = analyze_graph(
                    graph_context
                )


            st.markdown(ai_result)