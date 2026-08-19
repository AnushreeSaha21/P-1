"""
Neo4j network analysis service.

This module performs network analysis directly against Neo4j.

PostgreSQL remains the source database.
Neo4j is used only for the network-analysis layer.
"""

from backend.network_analysis.neo4j_connection import (
    get_neo4j_database,
    get_neo4j_driver,
)


GRAPH_NAME = "fiu_pan_network"


# =========================================================
# INTERNAL QUERY HELPER
# =========================================================

def _run(
    query,
    parameters=None,
):

    driver = get_neo4j_driver()

    records, summary, keys = driver.execute_query(
        query,
        parameters_=parameters or {},
        database_=get_neo4j_database(),
    )

    return records


# =========================================================
# NETWORK SUMMARY
# =========================================================

def get_network_summary():

    pan_records = _run(
        """
        MATCH (p:PAN)

        RETURN count(p) AS pan_count
        """
    )

    relationship_records = _run(
        """
        MATCH ()-[r:TRANSACTS_TO]->()

        RETURN count(r) AS relationship_count
        """
    )

    pan_count = (
        pan_records[0]["pan_count"]
        if pan_records
        else 0
    )

    relationship_count = (
        relationship_records[0]["relationship_count"]
        if relationship_records
        else 0
    )

    return {

        "pans": pan_count,

        "relationships": relationship_count,

        "connected_components": None

    }
# =========================================================
# CIRCULAR TRANSACTION PATTERNS
# =========================================================

def find_transaction_cycles(
    max_cycle_length=5,
    limit=100
):
    """
    Find directed transaction cycles in Neo4j.

    Cycles of length 2 through max_cycle_length
    are considered.

    The returned structure intentionally matches
    the structure previously produced by NetworkX.
    """

    max_cycle_length = int(
        max_cycle_length
    )

    if max_cycle_length < 2:

        return []

    if max_cycle_length > 10:

        max_cycle_length = 10

    limit = int(limit)

    if limit < 1:

        return []

    query = f"""
        MATCH p = (
            start:PAN
        )-[rels:TRANSACTS_TO*2..{max_cycle_length}]->(
            start
        )

        RETURN
            [n IN nodes(p) | n.pan] AS pans,

            [
                r IN rels |
                {{
                    source: startNode(r).pan,
                    target: endNode(r).pan,
                    transactions: coalesce(
                        r.transactions,
                        0
                    ),
                    alerts: coalesce(
                        r.alerts,
                        0
                    ),
                    isins: coalesce(
                        r.isins,
                        []
                    ),
                    alert_periods: coalesce(
                        r.alert_periods,
                        []
                    ),
                    min_period: r.min_period
                }}
            ] AS relationships

        LIMIT $query_limit
    """

    records = _run(
        query,
        {
            "query_limit": max(
                limit * 20,
                100
            )
        }
    )

    cycles = []

    seen = set()

    for record in records:

        raw_pans = list(
            record["pans"] or []
        )

        # The starting PAN appears again
        # at the end of the returned cycle.
        if (
            len(raw_pans) < 3
            or raw_pans[0] != raw_pans[-1]
        ):
            continue

        cycle_nodes = raw_pans[:-1]

        cycle_length = len(
            cycle_nodes
        )

        if cycle_length < 2:
            continue

        if cycle_length > max_cycle_length:
            continue

        # -------------------------------------------------
        # Ensure this is a simple cycle.
        # -------------------------------------------------

        if len(
            set(cycle_nodes)
        ) != len(cycle_nodes):

            continue

        # -------------------------------------------------
        # Normalize rotation.
        # -------------------------------------------------

        normalized = min(
            tuple(
                cycle_nodes[i:]
                +
                cycle_nodes[:i]
            )
            for i in range(
                len(cycle_nodes)
            )
        )

        if normalized in seen:

            continue

        seen.add(
            normalized
        )

        raw_relationships = list(
            record["relationships"] or []
        )

        relationships = []

        for relationship in raw_relationships:

            isins = sorted({
                str(isin).strip().upper()
                for isin in (
                    relationship.get(
                        "isins",
                        []
                    )
                    or []
                )
                if isin
            })

            alert_periods = [
                str(period)
                for period in (
                    relationship.get(
                        "alert_periods",
                        []
                    )
                    or []
                )
                if period
            ]

            # Preserve the old UI expectation that
            # "alerts" behaves like a list.
            alerts = [
                {
                    "period": period
                }
                for period in alert_periods
            ]

            relationships.append({

                "source": relationship[
                    "source"
                ],

                "target": relationship[
                    "target"
                ],

                "transactions": int(
                    relationship.get(
                        "transactions",
                        0
                    )
                    or 0
                ),

                "alerts": alerts,

                "isins": isins,

                "alert_periods": alert_periods,

                "min_period": relationship.get(
                    "min_period"
                )

            })

        # -------------------------------------------------
        # ISIN information
        # -------------------------------------------------

        cycle_isins = sorted({

            isin

            for relationship in relationships

            for isin in relationship[
                "isins"
            ]

        })

        common_isins = None

        for relationship in relationships:

            relationship_isins = set(
                relationship[
                    "isins"
                ]
            )

            if common_isins is None:

                common_isins = (
                    relationship_isins
                )

            else:

                common_isins &= (
                    relationship_isins
                )

        common_isins = sorted(
            common_isins or []
        )

        # -------------------------------------------------
        # Chronological observation
        # -------------------------------------------------

        chronological = True

        previous_period = None

        for relationship in relationships:

            current_period = relationship.get(
                "min_period"
            )

            if current_period is None:

                chronological = False
                break

            if (
                previous_period is not None
                and current_period < previous_period
            ):

                chronological = False
                break

            previous_period = (
                current_period
            )

        cycles.append({

            "PANs": list(
                normalized
            ),

            "Length": cycle_length,

            "relationships": relationships,

            "ISINs": cycle_isins,

            "Common_ISINs": common_isins,

            "Chronological": chronological

        })

        if len(cycles) >= limit:

            break

    return cycles


# =========================================================
# RECIPROCAL RELATIONSHIPS
# =========================================================

def find_reciprocal_relationships(
    limit=100
):
    """
    Find PAN pairs where:

        A → B

    and

        B → A

    both exist.
    """

    records = _run(
        """
        MATCH
            (source:PAN)
            -[forward:TRANSACTS_TO]->
            (target:PAN)

        MATCH
            (target)
            -[reverse:TRANSACTS_TO]->
            (source)

        WHERE
            source.pan < target.pan

        RETURN
            source.pan AS source,
            target.pan AS target,

            coalesce(
                forward.transactions,
                0
            ) AS forward_transactions,

            coalesce(
                reverse.transactions,
                0
            ) AS reverse_transactions,

            coalesce(
                forward.isins,
                []
            ) AS forward_isins,

            coalesce(
                reverse.isins,
                []
            ) AS reverse_isins,

            coalesce(
                forward.alert_periods,
                []
            ) AS forward_alert_periods,

            coalesce(
                reverse.alert_periods,
                []
            ) AS reverse_alert_periods

        LIMIT $limit
        """,
        {
            "limit": int(limit)
        }
    )

    relationships = []

    for record in records:

        relationships.append({

            "source": record[
                "source"
            ],

            "target": record[
                "target"
            ],

            "forward_transactions": int(
                record[
                    "forward_transactions"
                ]
                or 0
            ),

            "reverse_transactions": int(
                record[
                    "reverse_transactions"
                ]
                or 0
            ),

            "forward_isins": sorted({
                str(isin).strip().upper()
                for isin in (
                    record[
                        "forward_isins"
                    ]
                    or []
                )
                if isin
            }),

            "reverse_isins": sorted({
                str(isin).strip().upper()
                for isin in (
                    record[
                        "reverse_isins"
                    ]
                    or []
                )
                if isin
            }),

            "forward_alert_periods": [
                str(period)
                for period in (
                    record[
                        "forward_alert_periods"
                    ]
                    or []
                )
            ],

            "reverse_alert_periods": [
                str(period)
                for period in (
                    record[
                        "reverse_alert_periods"
                    ]
                    or []
                )
            ]

        })

    return relationships


# =========================================================
# SELF LOOPS
# =========================================================

def find_self_loops(
    limit=100
):
    """
    Find transactions where:

        PAN A → PAN A
    """

    records = _run(
        """
        MATCH
            (pan:PAN)
            -[relationship:TRANSACTS_TO]->
            (pan)

        RETURN
            pan.pan AS pan,

            coalesce(
                relationship.transactions,
                0
            ) AS transactions,

            coalesce(
                relationship.isins,
                []
            ) AS isins,

            coalesce(
                relationship.alert_periods,
                []
            ) AS alert_periods

        LIMIT $limit
        """,
        {
            "limit": int(limit)
        }
    )

    results = []

    for record in records:

        results.append({

            "pan": record["pan"],

            "transactions": int(
                record["transactions"]
                or 0
            ),

            "isins": sorted({
                str(isin).strip().upper()
                for isin in (
                    record["isins"]
                    or []
                )
                if isin
            }),

            "alert_periods": [
                str(period)
                for period in (
                    record[
                        "alert_periods"
                    ]
                    or []
                )
            ]

        })

    return results


# =========================================================
# PAN PATH SEARCH
# =========================================================

def find_pan_path(
    source_pan,
    target_pan,
    max_hops=5
):
    """
    Find the shortest directed transaction path
    between two PANs.

    Supports:
        A → B
        B → A
        A → A self-loops
        A → B → C → A circular paths

    The primary investigation search is limited
    to max_hops.

    If no path is found within max_hops, a second
    bounded search checks whether a longer path exists.
    """

    source_pan = (
        source_pan
        .strip()
        .upper()
    )

    target_pan = (
        target_pan
        .strip()
        .upper()
    )

    max_hops = int(max_hops)

    if not source_pan or not target_pan:
        return None

    if max_hops < 1:
        max_hops = 1

    # =====================================================
    # Helper: convert Neo4j relationships to application data
    # =====================================================

    def _build_result(record):

        path = list(
            record["path"] or []
        )

        relationships = []

        for relationship in (
            record["relationships"] or []
        ):

            relationships.append({

                "source": relationship[
                    "source"
                ],

                "target": relationship[
                    "target"
                ],

                "transactions": int(
                    relationship.get(
                        "transactions",
                        0
                    )
                    or 0
                ),

                "alerts": int(
                    relationship.get(
                        "alerts",
                        0
                    )
                    or 0
                ),

                "isins": sorted({

                    str(isin)
                    .strip()
                    .upper()

                    for isin in (
                        relationship.get(
                            "isins",
                            []
                        )
                        or []
                    )

                    if isin

                }),

                "alert_periods": [

                    str(period)

                    for period in (
                        relationship.get(
                            "alert_periods",
                            []
                        )
                        or []
                    )

                ]

            })

        return {

            "path": path,

            "hops": len(path) - 1,

            "relationships": relationships,

            "exceeds_limit": False

        }

    # =====================================================
    # Primary search
    # =====================================================

    query = f"""
        MATCH p =
            (source:PAN {{
                pan: $source
            }})
            -[:TRANSACTS_TO*1..{max_hops}]->
            (target:PAN {{
                pan: $target
            }})

        RETURN

            [n IN nodes(p) | n.pan]
                AS path,

            [
                r IN relationships(p) |
                {{
                    source: startNode(r).pan,

                    target: endNode(r).pan,

                    transactions: coalesce(
                        r.transactions,
                        0
                    ),

                    alerts: coalesce(
                        r.alerts,
                        0
                    ),

                    isins: coalesce(
                        r.isins,
                        []
                    ),

                    alert_periods: coalesce(
                        r.alert_periods,
                        []
                    )
                }}
            ]
            AS relationships

        ORDER BY length(p)

        LIMIT 1
    """

    records = _run(
        query,
        {
            "source": source_pan,
            "target": target_pan
        }
    )

    if records:

        return _build_result(
            records[0]
        )

    # =====================================================
    # No path within limit
    #
    # Check whether a longer path exists.
    #
    # We deliberately use a bounded upper limit rather
    # than an unrestricted variable-length path.
    # =====================================================

    extended_limit = max(
        max_hops + 10,
        max_hops * 2
    )

    extended_query = f"""
        MATCH p =
            (source:PAN {{
                pan: $source
            }})
            -[:TRANSACTS_TO*1..{extended_limit}]->
            (target:PAN {{
                pan: $target
            }})

        WHERE length(p) > {max_hops}

        RETURN

            length(p)
                AS hops

        ORDER BY length(p)

        LIMIT 1
    """

    extended_records = _run(
        extended_query,
        {
            "source": source_pan,
            "target": target_pan
        }
    )

    if extended_records:

        return {

            "path": [],

            "hops": int(
                extended_records[0]["hops"]
            ),

            "relationships": [],

            "exceeds_limit": True

        }

    return None

# =========================================================
# PAN EXPLORER
# =========================================================

def find_pan_neighbors(
    pan
):
    """
    Return only immediate incoming and outgoing
    relationships for the supplied PAN.
    """

    pan = (
        pan
        .strip()
        .upper()
    )

    if not pan:

        return None

    # -----------------------------------------------------
    # Verify PAN exists
    # -----------------------------------------------------

    records = _run(
        """
        MATCH (pan:PAN {
            pan: $pan
        })

        RETURN pan.pan AS pan
        LIMIT 1
        """,
        {
            "pan": pan
        }
    )

    if not records:

        return None

    # -----------------------------------------------------
    # Incoming
    # -----------------------------------------------------

    incoming_records = _run(
        """
        MATCH
            (source:PAN)
            -[relationship:TRANSACTS_TO]->
            (target:PAN {
                pan: $pan
            })

        RETURN
            source.pan AS source,
            target.pan AS target,

            coalesce(
                relationship.transactions,
                0
            ) AS transactions,

            coalesce(
                relationship.alerts,
                0
            ) AS alerts,

            coalesce(
                relationship.isins,
                []
            ) AS isins,

            coalesce(
                relationship.alert_periods,
                []
            ) AS alert_periods
        """,
        {
            "pan": pan
        }
    )

    # -----------------------------------------------------
    # Outgoing
    # -----------------------------------------------------

    outgoing_records = _run(
        """
        MATCH
            (source:PAN {
                pan: $pan
            })
            -[relationship:TRANSACTS_TO]->
            (target:PAN)

        RETURN
            source.pan AS source,
            target.pan AS target,

            coalesce(
                relationship.transactions,
                0
            ) AS transactions,

            coalesce(
                relationship.alerts,
                0
            ) AS alerts,

            coalesce(
                relationship.isins,
                []
            ) AS isins,

            coalesce(
                relationship.alert_periods,
                []
            ) AS alert_periods
        """,
        {
            "pan": pan
        }
    )

    incoming = []

    for record in incoming_records:

        incoming.append({

            "source": record["source"],

            "target": record["target"],

            "transactions": int(
                record["transactions"]
                or 0
            ),

            "alerts": int(
                record["alerts"]
                or 0
            ),

            "isins": sorted({
                str(isin).strip().upper()
                for isin in (
                    record["isins"]
                    or []
                )
                if isin
            }),

            "alert_periods": [
                str(period)
                for period in (
                    record[
                        "alert_periods"
                    ]
                    or []
                )
            ]

        })

    outgoing = []

    for record in outgoing_records:

        outgoing.append({

            "source": record["source"],

            "target": record["target"],

            "transactions": int(
                record["transactions"]
                or 0
            ),

            "alerts": int(
                record["alerts"]
                or 0
            ),

            "isins": sorted({
                str(isin).strip().upper()
                for isin in (
                    record["isins"]
                    or []
                )
                if isin
            }),

            "alert_periods": [
                str(period)
                for period in (
                    record[
                        "alert_periods"
                    ]
                    or []
                )
            ]

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