import networkx as nx


def build_graph(rows):
    """
    Build PAN relationship graph.

    Parameters
    ----------
    rows : iterable

    Each row should contain:
        source_pan,
        source_name,
        target_pan,
        target_name

    Returns
    -------
    networkx.Graph
    """

    G = nx.DiGraph()

    for row in rows:

        source_pan = row["source_pan"]
        source_name = row["source_name"]

        target_pan = row["target_pan"]
        target_name = row["target_name"]

        # Clean values
        if source_pan:
            source_pan = source_pan.strip().upper()

        if target_pan:
            target_pan = target_pan.strip().upper()

        INVALID = {"", "NAN", "NONE", "NULL"}

        if source_pan in INVALID:
            source_pan = None

        if target_pan in INVALID:
            target_pan = None

        # -------------------------
        # Source node
        # -------------------------

        if source_pan:

            if not G.has_node(source_pan):

                G.add_node(
                    source_pan,
                    name=source_name
                )

        # -------------------------
        # Target node
        # -------------------------

        if target_pan:

            if not G.has_node(target_pan):

                G.add_node(
                    target_pan,
                    name=target_name
                )

        # -------------------------
        # Relationship
        # -------------------------

        if source_pan and target_pan:

            if G.has_edge(source_pan, target_pan):

                G[source_pan][target_pan]["transactions"] += 1

            else:

                    G.add_edge(
                        source_pan,
                        target_pan,
                        transactions=1
                    )

    return G


def get_neighbors(graph, pan):
    """
    Returns all PANs directly connected to the given PAN.
    """

    pan = pan.strip().upper()

    if pan not in graph:
        return []

    return sorted(graph.neighbors(pan))

def get_degree(graph, pan):
    """
    Number of direct neighbours.
    """

    if pan not in graph:
        return 0

    return graph.degree(pan)

def get_component(graph, pan):
    """
    Returns every PAN connected to this PAN.
    """

    if pan not in graph:
        return []

    for component in nx.weakly_connected_components(graph):
        if pan in component:
            return sorted(component)

    return []


def build_subgraph(graph, pan):
    """
    Returns the connected component containing the PAN.
    """

    pan = pan.strip().upper()

    if pan not in graph:
        return None

    component = None

    for comp in nx.weakly_connected_components(graph):
        if pan in comp:
            component = comp
            break

    if component is None:
        return None

    return graph.subgraph(component).copy()


def get_top_hubs(graph, limit=10):
    """
    PANs having the highest number of connections.
    """

    hubs = []

    for node in graph.nodes():

        hubs.append({
            "pan": node,
            "name": graph.nodes[node].get("name", ""),
            "connections": graph.degree(node)
        })

    hubs.sort(
        key=lambda x: x["connections"],
        reverse=True
    )

    return hubs[:limit]


def get_flow(graph, pan):
    """
    Incoming vs outgoing relationships.
    """

    pan = pan.strip().upper()

    if pan not in graph:
        return None

    return {

        "incoming": graph.in_degree(pan),

        "outgoing": graph.out_degree(pan)

    }


def get_top_relationships(graph, limit=10):
    """
    Highest transaction relationships.
    """

    edges = []

    for source, target, data in graph.edges(data=True):

        edges.append({

            "source": source,

            "target": target,

            "transactions": data.get("transactions", 1)

        })

    edges.sort(

        key=lambda x: x["transactions"],

        reverse=True

    )

    return edges[:limit]