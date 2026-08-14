import networkx as nx

from backend.database.db_connection import get_connection

from backend.network_analysis.network_repository import (
    get_pan_relationships
)


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

                "report_fortnight": report_fortnight

            })


        # -------------------------------------------------
        # New relationship
        # -------------------------------------------------

        else:

            graph.add_edge(

                source_pan,

                target_pan,

                transactions=1,

                alerts=[{

                    "fiu_alert_type": fiu_alert_type,

                    "report_year": report_year,

                    "report_month": report_month,

                    "report_fortnight": report_fortnight

                }]

            )

    return graph


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


            relationships.append({

                "source": source,

                "target": target,

                "transactions": edge_data.get(
                    "transactions",
                    0
                ),

                "alerts": edge_data.get(
                    "alerts",
                    []
                )

            })


        cycles.append({

            "PANs": list(normalized),

            "Length": cycle_length,

            "relationships": relationships

        })


        if len(cycles) >= limit:
            break


    return cycles