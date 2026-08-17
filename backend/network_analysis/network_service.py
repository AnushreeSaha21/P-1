import networkx as nx

from backend.database.db_connection import get_connection

from backend.network_analysis.network_repository import (
    get_pan_relationships
)

from pyvis.network import Network


def build_cycle_visualization(graph):

    network = Network(
        height="650px",
        width="100%",
        directed=True,
        bgcolor="#0E1117",
        font_color="white"
    )

    network.set_options("""
    {
        "interaction": {
            "hover": true,
            "zoomView": true,
            "dragView": true,
            "navigationButtons": true
        },

        "physics": {
            "enabled": true,
            "stabilization": {
                "iterations": 100
            }
        },

        "edges": {
            "arrows": {
                "to": {
                    "enabled": true
                }
            },

            "smooth": {
                "enabled": true,
                "type": "curvedCW"
            },

            "font": {
                "size": 10,
                "color": "#B8B8B8",
                "face": "Arial",
                "strokeWidth": 0
            }
        },

        "nodes": {
            "shape": "dot",
            "size": 25,

            "font": {
                "size": 14,
                "color": "white",
                "face": "Arial"
            }
        }
    }
    """)

    # ---------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------

    for node in graph.nodes():

        network.add_node(
            node,
            label=node,
            title=f"PAN: {node}",
            size=30
        )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    for source, target, data in graph.edges(
    data=True
):

        transactions = data.get(
            "transactions",
            0
        )

        alerts = data.get(
            "alerts",
            []
        )

        isins = sorted({
            alert.get("isin_code")
            for alert in alerts
            if alert.get("isin_code")
        })

        isin_text = (
            ", ".join(isins)
            if isins
            else "Not available"
        )

        alert_periods = []

        for alert in alerts:

            year = alert.get("report_year")
            month = alert.get("report_month")
            fortnight = alert.get("report_fortnight")

            if (
                year is not None
                and month is not None
                and fortnight is not None
            ):

                alert_periods.append(
                    f"{year}-{month:02d} - "
                    f"{fortnight} Fortnight"
                )

        alert_periods = sorted(
            set(alert_periods)
        )

        period_text = (
            "\n".join(alert_periods)
            if alert_periods
            else "Not available"
        )

        network.add_edge(
            source,
            target,

            label=f"{transactions} txn",

            title=(
                f"{source} → {target}\n"
                f"Transactions: {transactions}\n"
                f"ISINs: {isin_text}\n"
                f"Alert Periods:\n{period_text}"
            ),

            arrows="to",

            font={
                "size": 10,
                "color": "#A8A8A8",
                "face": "Arial",
                "strokeWidth": 0
            }
        )

    return network

def build_analysis_graph():

    connection = get_connection()

    try:

        rows = get_pan_relationships(
            connection
        )

    finally:

        connection.close()


    graph = nx.DiGraph()

    for row in rows:

        source_pan = row[0]
        target_pan = row[1]
        fiu_alert_type = row[2]
        report_year = row[3]
        report_month = row[4]
        report_fortnight = row[5]
        isin_code = row[6]

        if source_pan is None or target_pan is None:
            continue

        source_pan = source_pan.strip().upper()
        target_pan = target_pan.strip().upper()

        if not source_pan or not target_pan:
            continue


        # -------------------------------------------------
        # Existing relationship
        # -------------------------------------------------

        if graph.has_edge(
            source_pan,
            target_pan
        ):

            edge = graph[
                source_pan
            ][
                target_pan
            ]

            edge["transactions"] += 1

            edge["alerts"].append({

                "fiu_alert_type": fiu_alert_type,

                "report_year": report_year,

                "report_month": report_month,

                "report_fortnight": report_fortnight,

                "isin_code": isin_code

            })

            if (
                isin_code
                and str(isin_code).strip()
                and str(isin_code).strip().lower()
                not in ["nan", "none", "null"]
            ):

                isin_code = str(
                    isin_code
                ).strip().upper()

                if isin_code not in edge["isins"]:

                    edge["isins"].append(
                        isin_code
                    )


        # -------------------------------------------------
        # New relationship
        # -------------------------------------------------

        else:

            isins = []

            if (
                isin_code
                and str(isin_code).strip()
                and str(isin_code).strip().lower()
                not in ["nan", "none", "null"]
            ):

                isins.append(
                    str(
                        isin_code
                    ).strip().upper()
                )

            graph.add_edge(

                source_pan,

                target_pan,

                transactions=1,

                isins=isins,

                alerts=[{

                    "fiu_alert_type": fiu_alert_type,

                    "report_year": report_year,

                    "report_month": report_month,

                    "report_fortnight": report_fortnight,

                    "isin_code": isin_code

                }]

            )

    return graph

def get_period_key(alert):

    year = alert.get("report_year")
    month = alert.get("report_month")
    fortnight = alert.get("report_fortnight")

    if year is None or month is None or fortnight is None:
        return None

    try:

        return (
            int(year),
            int(month),
            int(fortnight)
        )

    except (TypeError, ValueError):

        return None

def find_transaction_cycles(
    graph,
    max_cycle_length=5,
    limit=100
):
    """
    Find directed transaction cycles and
    return the relationship information
    contained within each cycle.
    """

    cycles = []

    seen = set()

    for cycle in nx.simple_cycles(graph):

        cycle_length = len(cycle)

        if cycle_length < 2:
            continue

        if cycle_length > max_cycle_length:
            continue


        # -------------------------------------------------
        # Normalize cycle
        # -------------------------------------------------

        normalized = min(
            tuple(
                cycle[i:] + cycle[:i]
            )
            for i in range(
                len(cycle)
            )
        )

        if normalized in seen:
            continue

        seen.add(normalized)


        # -------------------------------------------------
        # Build cycle relationships
        # -------------------------------------------------

        relationships = []

        for i in range(
            len(normalized)
        ):

            source = normalized[i]

            target = normalized[
                (i + 1) % len(normalized)
            ]

            edge_data = graph[
                source
            ][
                target
            ]


            edge_alerts = edge_data.get(
                "alerts",
                []
            )

            isins = sorted({
                alert["isin_code"]
                for alert in edge_alerts
                if alert.get("isin_code")
                and str(alert["isin_code"]).strip()
            })

            relationships.append({

                "source": source,

                "target": target,

                "transactions": edge_data.get(
                    "transactions",
                    0
                ),

                "alerts": edge_alerts,

                "isins": isins

            })

        cycle_isins = sorted({
                isin
                for relationship in relationships
                for isin in relationship["isins"]
            })

        common_isins = None

        for relationship in relationships:

            relationship_isins = set(
                relationship["isins"]
            )

            if common_isins is None:

                common_isins = relationship_isins

            else:

                common_isins &= relationship_isins

        common_isins = sorted(
            common_isins or []
        )

        cycle_periods = []

        for relationship in relationships:

            relationship_periods = []

            for alert in relationship["alerts"]:

                period = get_period_key(alert)

                if period is not None:

                    relationship_periods.append(period)

            cycle_periods.append(
                relationship_periods
            )


        chronological = True

        previous_period = None

        for relationship_periods in cycle_periods:

            if not relationship_periods:
                chronological = False
                break

            current_period = min(
                relationship_periods
            )

            if (
                previous_period is not None
                and current_period < previous_period
            ):

                chronological = False
                break

            previous_period = current_period


        cycles.append({

            "PANs": list(normalized),

            "Length": cycle_length,

            "relationships": relationships,

            "ISINs": cycle_isins,

            "Common_ISINs": common_isins,

            "Chronological": chronological

        })


        if len(cycles) >= limit:
            break


    return cycles

def find_pan_neighbors(
    graph,
    pan
):
    """
    Return only the immediate incoming and outgoing
    relationships for the supplied PAN.
    """

    pan = pan.strip().upper()

    if pan not in graph:

        return None

    incoming = []
    outgoing = []

    # =========================================================
    # INCOMING
    # =========================================================

    for source in graph.predecessors(pan):

        data = graph[
            source
        ][
            pan
        ]

        incoming.append({

            "source": source,

            "target": pan,

            "transactions": data.get(
                "transactions",
                0
            ),

            "isins": data.get(
                "isins",
                []
            ),

            "alerts": data.get(
                "alerts",
                []
            )

        })

    # =========================================================
    # OUTGOING
    # =========================================================

    for target in graph.successors(pan):

        data = graph[
            pan
        ][
            target
        ]

        outgoing.append({

            "source": pan,

            "target": target,

            "transactions": data.get(
                "transactions",
                0
            ),

            "isins": data.get(
                "isins",
                []
            ),

            "alerts": data.get(
                "alerts",
                []
            )

        })

    return {

        "pan": pan,

        "incoming": incoming,

        "outgoing": outgoing,

        "total_connections": (
            len(incoming)
            +
            len(outgoing)
        )

    }



def build_pan_visualization(
    graph,
    pan
):

    pan = pan.strip().upper()

    if pan not in graph:

        return None

    network = Network(
        height="650px",
        width="100%",
        directed=True,
        bgcolor="#0E1117",
        font_color="white"
    )

    network.set_options("""
    {
        "interaction": {
            "hover": true,
            "zoomView": true,
            "dragView": true,
            "navigationButtons": true,
            "hideEdgesOnDrag": true
        },

        "physics": {
            "enabled": true,
            "stabilization": {
                "enabled": true,
                "iterations": 150,
                "fit": true
            },
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -80,
                "centralGravity": 0.01,
                "springLength": 150,
                "springConstant": 0.05,
                "damping": 0.8,
                "avoidOverlap": 1
            }
        },

        "edges": {

            "arrows": {
                "to": {
                    "enabled": true
                }
            },

            "smooth": {
                "enabled": true,
                "type": "curvedCW"
            },

            "font": {
                "size": 10,
                "color": "#A8A8A8",
                "face": "Arial",
                "strokeWidth": 0
            }
        },

        "nodes": {

            "shape": "dot",

            "size": 25,

            "font": {
                "size": 14,
                "color": "white",
                "face": "Arial"
            }
        }
    }
    """)

    # =========================================================
    # CENTRAL PAN
    # =========================================================

    network.add_node(
        pan,
        label=pan,
        size=35,
        color={
            "background": "#FFD54F",
            "border": "#FFB300",
            "highlight": {
                "background": "#FFE082",
                "border": "#FFB300"
            }
        },
        font={
            "color": "#111111",
            "size": 16
        }
    )

    # =========================================================
    # INCOMING
    # =========================================================

    for source in graph.predecessors(pan):

        data = graph[
            source
        ][
            pan
        ]

        transactions = data.get(
            "transactions",
            0
        )

        isins = data.get(
            "isins",
            []
        )

        isin_text = (
            ", ".join(isins)
            if isins
            else "Not available"
        )

        alerts = data.get(
            "alerts",
            []
        )

        alert_periods = []

        for alert in alerts:

            year = alert.get("report_year")
            month = alert.get("report_month")
            fortnight = alert.get("report_fortnight")

            if (
                year is not None
                and month is not None
                and fortnight is not None
            ):

                alert_periods.append(
                    f"{year}-{month:02d} - "
                    f"{fortnight} Fortnight"
                )

        alert_periods = sorted(
            set(alert_periods)
        )

        period_text = (
            "\n".join(alert_periods)
            if alert_periods
            else "Not available"
        )

        network.add_node(
            source,
            label=source,
            color={
                "background": "#8AB4F8",
                "border": "#6EA8FE"
            }
        )

        network.add_edge(

            source,

            pan,

            label=f"{transactions} txn",

            title=(
                f"{source} → {pan}\n"
                f"Transactions: {transactions}\n"
                f"ISINs: {isin_text}\n"
                f"Alert Periods:\n{period_text}"
            ),

            arrows="to",

            font={
                "size": 10,
                "color": "#A8A8A8",
                "face": "Arial",
                "strokeWidth": 0
            }

        )

    # =========================================================
    # OUTGOING
    # =========================================================

    for target in graph.successors(pan):

        data = graph[
            pan
        ][
            target
        ]

        transactions = data.get(
            "transactions",
            0
        )

        isins = data.get(
            "isins",
            []
        )

        isin_text = (
            ", ".join(isins)
            if isins
            else "Not available"
        )

        alerts = data.get(
            "alerts",
            []
        )

        alert_periods = []

        for alert in alerts:

            year = alert.get("report_year")
            month = alert.get("report_month")
            fortnight = alert.get("report_fortnight")

            if (
                year is not None
                and month is not None
                and fortnight is not None
            ):

                alert_periods.append(
                    f"{year}-{month:02d} - "
                    f"{fortnight} Fortnight"
                )

        alert_periods = sorted(
            set(alert_periods)
        )

        period_text = (
            "\n".join(alert_periods)
            if alert_periods
            else "Not available"
        )

        network.add_node(
            target,
            label=target,
            color={
                "background": "#8AB4F8",
                "border": "#6EA8FE"
            }
        )

        network.add_edge(

            pan,

            target,

            label=f"{transactions} txn",

            title=(
                f"{pan} → {target}\n"
                f"Transactions: {transactions}\n"
                f"ISINs: {isin_text}\n"
                f"Alert Periods:\n{period_text}"
            ),

            arrows="to",

            font={
                "size": 10,
                "color": "#A8A8A8",
                "face": "Arial",
                "strokeWidth": 0
            }

        )

    return network


def find_reciprocal_relationships(
    graph,
    limit=100
):
    """
    Find PAN pairs where transactions exist
    in both directions:

        A -> B
        B -> A
    """

    relationships = []

    seen = set()

    for source, target, data in graph.edges(data=True):

        if not graph.has_edge(target, source):
            continue

        pair = tuple(
            sorted([source, target])
        )

        if pair in seen:
            continue

        seen.add(pair)

        reverse_data = graph[
            target
        ][
            source
        ]

        forward_alerts = data.get(
            "alerts",
            []
        )

        reverse_alerts = reverse_data.get(
            "alerts",
            []
        )

        forward_isins = sorted({
            alert.get("isin_code")
            for alert in forward_alerts
            if alert.get("isin_code")
        })

        reverse_isins = sorted({
            alert.get("isin_code")
            for alert in reverse_alerts
            if alert.get("isin_code")
        })

        relationships.append({

            "source": source,

            "target": target,

            "forward_transactions": data.get(
                "transactions",
                0
            ),

            "reverse_transactions": reverse_data.get(
                "transactions",
                0
            ),

            "forward_alerts": len(
                forward_alerts
            ),

            "reverse_alerts": len(
                reverse_alerts
            ),

            "forward_isins": forward_isins,

            "reverse_isins": reverse_isins

        })

        if len(relationships) >= limit:
            break

    return relationships



def find_pan_path(
    graph,
    source_pan,
    target_pan,
    max_hops=5
):
    """
    Find a directed transaction path between
    two PANs.

    Returns the shortest path within the
    configured hop limit.
    """

    source_pan = source_pan.strip().upper()
    target_pan = target_pan.strip().upper()

    if source_pan not in graph:
        return None

    if target_pan not in graph:
        return None

    if source_pan == target_pan:
        return {
            "path": [source_pan],
            "hops": 0,
            "relationships": []
        }

    try:

        path = nx.shortest_path(
            graph,
            source=source_pan,
            target=target_pan
        )

    except nx.NetworkXNoPath:

        return None

    hops = len(path) - 1

    if hops > max_hops:

        return {
            "path": path,
            "hops": hops,
            "relationships": [],
            "exceeds_limit": True
        }

    relationships = []

    for i in range(len(path) - 1):

        source = path[i]
        target = path[i + 1]

        edge_data = graph[
            source
        ][
            target
        ]

        alerts = edge_data.get(
            "alerts",
            []
        )

        isins = sorted({
            alert.get("isin_code")
            for alert in alerts
            if alert.get("isin_code")
        })

        relationships.append({

            "source": source,

            "target": target,

            "transactions": edge_data.get(
                "transactions",
                0
            ),

            "alerts": len(alerts),

            "isins": isins

        })

    return {

        "path": path,

        "hops": hops,

        "relationships": relationships,

        "exceeds_limit": False

    }