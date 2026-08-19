"""
Synchronize the PAN relationship model from PostgreSQL into Neo4j.

Run from the project root:

    python -m backend.network_analysis.sync_neo4j

This script is intentionally separate from Streamlit so the app
does not reload the entire PostgreSQL network on every page rerun.
"""

from backend.database.db_connection import get_connection

from backend.network_analysis.neo4j_connection import (
    get_neo4j_database,
    get_neo4j_driver,
)

from backend.network_analysis.neo4j_service import (
    GRAPH_NAME,
)


RELATIONSHIP_QUERY = """
SELECT
    BTRIM(source_pan) AS source_pan,
    BTRIM(target_pan) AS target_pan,

    COUNT(*)::INTEGER AS transactions,

    COUNT(*)::INTEGER AS alerts,

    COALESCE(
        ARRAY_AGG(
            DISTINCT UPPER(
                BTRIM(isin_code)
            )
            ORDER BY UPPER(
                BTRIM(isin_code)
            )
        ) FILTER (
            WHERE
                isin_code IS NOT NULL
                AND BTRIM(isin_code) <> ''
                AND LOWER(BTRIM(isin_code))
                    NOT IN (
                        'nan',
                        'none',
                        'null'
                    )
        ),
        ARRAY[]::TEXT[]
    ) AS isins,

    COALESCE(
        ARRAY_AGG(
            DISTINCT CONCAT(
                report_year,
                '-',
                LPAD(
                    report_month::TEXT,
                    2,
                    '0'
                ),
                '-',
                report_fortnight
            )
            ORDER BY CONCAT(
                report_year,
                '-',
                LPAD(
                    report_month::TEXT,
                    2,
                    '0'
                ),
                '-',
                report_fortnight
            )
        ) FILTER (
            WHERE
                report_year IS NOT NULL
                AND report_month IS NOT NULL
                AND report_fortnight IS NOT NULL
        ),
        ARRAY[]::TEXT[]
    ) AS alert_periods,

    MIN(
        (
            report_year * 1000
        )
        +
        (
            report_month * 10
        )
        +
        report_fortnight
    ) AS min_period

FROM vw_alert_summary

WHERE
    source_pan IS NOT NULL
    AND target_pan IS NOT NULL

    AND BTRIM(source_pan) <> ''
    AND BTRIM(target_pan) <> ''

    AND LOWER(BTRIM(source_pan))
        NOT IN (
            'nan',
            'none',
            'null'
        )

    AND LOWER(BTRIM(target_pan))
        NOT IN (
            'nan',
            'none',
            'null'
        )

GROUP BY
    BTRIM(source_pan),
    BTRIM(target_pan)
"""


def _load_relationship_rows():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        try:

            cursor.execute(
                RELATIONSHIP_QUERY
            )

            rows = cursor.fetchall()

        finally:

            cursor.close()

    finally:

        connection.close()

    relationship_rows = []

    for row in rows:

        relationship_rows.append({
            "source": str(
                row[0]
            ).strip().upper(),

            "target": str(
                row[1]
            ).strip().upper(),

            "transactions": int(
                row[2] or 0
            ),

            "alerts": int(
                row[3] or 0
            ),

            "isins": [
                str(isin).strip().upper()
                for isin in (
                    row[4] or []
                )
                if isin
            ],

            "alert_periods": [
                str(period)
                for period in (
                    row[5] or []
                )
                if period
            ],

            "min_period": (
                int(row[6])
                if row[6] is not None
                else None
            ),
        })

    return relationship_rows


def _run(
    query,
    parameters=None,
):

    driver = get_neo4j_driver()

    return driver.execute_query(
        query,
        parameters_=parameters or {},
        database_=get_neo4j_database(),
    )


def _prepare_schema():

    _run(
        """
        CREATE CONSTRAINT pan_pan_unique
        IF NOT EXISTS
        FOR (p:PAN)
        REQUIRE p.pan IS UNIQUE
        """
    )


def _clear_graph():

    _run(
        """
        MATCH (p:PAN)
        DETACH DELETE p
        """
    )


def _write_relationship_batch(
    rows,
):

    if not rows:
        return

    _run(
        """
        UNWIND $rows AS row

        MERGE (source:PAN {pan: row.source})
        MERGE (target:PAN {pan: row.target})

        MERGE (source)-[r:TRANSACTS_TO]->(target)

        SET
            r.transactions = row.transactions,
            r.alerts = row.alerts,
            r.isins = row.isins,
            r.alert_periods = row.alert_periods,
            r.min_period = row.min_period
        """,
        {
            "rows": rows
        }
    )


def _refresh_gds_projection():

    try:

        exists_rows, _, _ = _run(
            """
            CALL gds.graph.exists(
                $graph_name
            )
            YIELD exists

            RETURN exists
            """,
            {
                "graph_name": GRAPH_NAME
            }
        )

        if (
            exists_rows
            and
            exists_rows[0]["exists"]
        ):
            _run(
                """
                CALL gds.graph.drop(
                    $graph_name
                )
                YIELD graphName

                RETURN graphName
                """,
                {
                    "graph_name": GRAPH_NAME
                }
            )

        _run(
            """
            MATCH
                (source:PAN)
                -[r:TRANSACTS_TO]->
                (target:PAN)

            RETURN gds.graph.project(
                $graph_name,
                source,
                target
            )
            """,
            {
                "graph_name": GRAPH_NAME
            }
        )

        print(
            "GDS WCC projection refreshed."
        )

    except Exception as exc:

        print(
            "GDS projection skipped: "
            f"{exc}"
        )


def sync():

    print(
        "Reading aggregated PAN relationships "
        "from PostgreSQL..."
    )

    rows = _load_relationship_rows()

    print(
        f"Relationships prepared: {len(rows)}"
    )

    _prepare_schema()
    _clear_graph()

    batch_size = 1000

    for start in range(
        0,
        len(rows),
        batch_size
    ):

        batch = rows[
            start:start + batch_size
        ]

        _write_relationship_batch(
            batch
        )

        print(
            f"Loaded "
            f"{min(start + batch_size, len(rows))}"
            f"/{len(rows)} relationships"
        )

    _refresh_gds_projection()

    print(
        "Neo4j network synchronization complete."
    )


if __name__ == "__main__":
    sync()
