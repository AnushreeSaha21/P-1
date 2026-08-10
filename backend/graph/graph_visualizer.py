from pyvis.network import Network


def build_pyvis_graph(graph, highlight_pan=None):

    net = Network(
        height="700px",
        width="100%",
        bgcolor="#0E1117",
        font_color="white",
        notebook=False,
        directed=True
    )

    # Smooth physics
        
    net.barnes_hut(
        gravity=-30000,
        central_gravity=0.2,
        spring_length=180,
        spring_strength=0.02,
        damping=0.09
    )

    # -----------------------
    # Nodes
    # -----------------------

    for node, data in graph.nodes(data=True):

        degree = graph.degree(node)

        
        if node == highlight_pan:

            color = "#E53935"      # Red
            size = 35

        elif degree >= 5:

            color = "#FB8C00"      # Orange
            size = 25

        else:

            color = "#43A047"      # Green
            size = 18

        net.add_node(

            node,

            label=node,

            color=color,

            size=size,

            font={
                "size": 18,
                "color": "white",
                "face": "Arial"
            },

            title=(
                f"PAN: {node}\n"
                f"Name: {data.get('name', '')}\n"
                f"Connections: {degree}"
            ),
            # size=12 + degree * 2
        )

    # -----------------------
    # Edges
    # -----------------------

    for source, target, data in graph.edges(data=True):

        net.add_edge(

            source,

            target,
            color="#94A3B8",
            width=2,

            value=data.get("transactions", 1),

            title=f"Transactions : {data.get('transactions',1)}",
            arrows="to"
        )
    
    return net