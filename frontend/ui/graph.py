import streamlit as st
import networkx as nx
import pandas as pd
import tempfile
from streamlit.components.v1 import html

from backend.graph.graph_service import (
    load_graph,
    search_pan,
    load_pyvis_graph,
    load_subgraph
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


    st.subheader("🔍 Explore PAN")

    pan = st.text_input("Enter PAN")

    st.subheader("🌐 Network Visualization")

    if st.button("Search PAN"):

        result = search_pan(graph, pan)

        if result is None:
            st.error("PAN not found.")
            st.stop()

        if result["degree"] == 0:
            st.info("This PAN has no connected PANs.")

        else:

            st.subheader(result["name"] or "Unknown Name")

            st.metric(
                "Neighbours",
                result["degree"]
            )

            neighbors_df = pd.DataFrame(
                result["neighbors"],
                columns=["Connected PAN"]
            )

            st.dataframe(
                neighbors_df,
                use_container_width=True
            )

            st.write(
                f"Connected Component: {len(result['component'])} PANs"
            )

            network = load_subgraph(graph, pan)

            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".html"
            )

            network.save_graph(tmp.name)
            print(tmp.name)

            with open(tmp.name, "r", encoding="utf-8") as f:
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

    