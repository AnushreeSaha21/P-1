import streamlit as st
import networkx as nx
import pandas as pd
import tempfile
from streamlit.components.v1 import html

from backend.graph.graph_service import (
    load_graph,
    search_pan,
    load_pyvis_graph,
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

                network = load_subgraph(
                    graph,
                    pan
                )

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

    