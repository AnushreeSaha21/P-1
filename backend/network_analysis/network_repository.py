def get_pan_relationships(connection):
    """
    Retrieve PAN-to-PAN relationships and the
    reporting information required for network analysis.
    """

    cursor = connection.cursor()

    try:

        query = """
            SELECT
                source_pan,
                target_pan,
                fiu_alert_type,
                report_year,
                report_month,
                report_fortnight

            FROM vw_alert_summary

            WHERE
                source_pan IS NOT NULL
                AND target_pan IS NOT NULL

                AND BTRIM(source_pan) <> ''
                AND BTRIM(target_pan) <> ''

                AND LOWER(BTRIM(source_pan))
                    NOT IN ('nan', 'none', 'null')

                AND LOWER(BTRIM(target_pan))
                    NOT IN ('nan', 'none', 'null')
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:

        cursor.close()