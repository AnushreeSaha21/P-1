import streamlit as st
from backend.database.db_connection import get_connection

from backend.graph.graph_repository import (
    get_graph_data
)

from backend.graph.graph_builder import (
    build_graph,
    get_neighbors,
    get_degree,
    get_component,
    build_subgraph,
    get_top_hubs,
    get_flow,
    get_top_relationships
)

from backend.graph.graph_visualizer import (
    build_pyvis_graph
)

@st.cache_resource
def load_graph():

    connection = get_connection()

    try:

        rows = get_graph_data(connection)

        graph = build_graph(rows)

        return graph

    finally:

        connection.close()


def search_pan(graph, pan):

    pan = pan.strip().upper()

    if pan not in graph:
        return None

    return {

        "name": graph.nodes[pan].get("name", ""),

        "degree": get_degree(graph, pan),

        "flow": get_flow(graph, pan),

        "neighbors": get_neighbors(graph, pan),

        "component": get_component(graph, pan)

    }

def load_pyvis_graph(graph):

    return build_pyvis_graph(graph)


def load_subgraph(graph, pan):

    subgraph = build_subgraph(graph, pan)

    if subgraph is None:
        st.error("PAN not found.")
        return

    return build_pyvis_graph(
        subgraph,
        highlight_pan=pan
    )

def load_top_hubs(graph):

    return get_top_hubs(graph)

def load_top_hubs(graph):

    return get_top_hubs(graph)

def load_flow(graph, pan):

    return get_flow(graph, pan)