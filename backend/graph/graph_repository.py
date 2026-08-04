from psycopg2.extensions import connection as PGConnection


def get_graph_data(connection: PGConnection):
    """
    Fetch PAN relationships from database.
    """

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT

                source_pan,
                source_name,

                target_pan,
                target_name

            FROM vw_alert_summary;
            """
        )

        columns = [
            "source_pan",
            "source_name",
            "target_pan",
            "target_name"
        ]

        rows = cursor.fetchall()

        result = []

        for row in rows:

            result.append(
                dict(zip(columns, row))
            )

        return result

    finally:

        cursor.close()