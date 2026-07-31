from psycopg2.extensions import connection as PGConnection


def get_top_cities(
    connection: PGConnection,
    limit=20
):
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                city,
                COUNT(*) AS total_alerts
            FROM
            (
                SELECT source_city AS city
                FROM vw_alert_summary
                WHERE source_city IS NOT NULL
                    AND BTRIM(source_city) <> ''
                    AND LOWER(BTRIM(source_city)) NOT IN ('nan', 'none', 'null')

                UNION ALL

                SELECT target_city AS city
                FROM vw_alert_summary
                WHERE source_city IS NOT NULL
                    AND BTRIM(target_city) <> ''
                    AND LOWER(BTRIM(target_city)) NOT IN ('nan', 'none', 'null')
            ) cities

            GROUP BY city

            ORDER BY
                total_alerts DESC,
                city

            LIMIT %s
            """,
            (limit,)
        )

        return cursor.fetchall()

    finally:
        cursor.close()


def get_monthly_trend(
    connection: PGConnection
):

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT

                report_year,

                report_month,

                COUNT(*) AS total_alerts

            FROM vw_alert_summary

            GROUP BY

                report_year,
                report_month

            ORDER BY

                report_year,
                report_month
            """
        )

        return cursor.fetchall()

    finally:

        cursor.close()

def get_top_pans(
    connection: PGConnection,
    limit=10
):

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT

                pan,

                COUNT(*) AS total_alerts

            FROM
            (
                SELECT source_pan AS pan
                FROM vw_alert_summary
                WHERE source_pan IS NOT NULL
                    AND BTRIM(source_pan) <> ''
                    AND LOWER(BTRIM(source_pan)) NOT IN ('nan', 'none', 'null')
                UNION ALL

                SELECT target_pan AS pan
                FROM vw_alert_summary
                WHERE target_pan IS NOT NULL
                    AND BTRIM(target_pan) <> ''
                    AND LOWER(BTRIM(target_pan)) NOT IN ('nan', 'none', 'null')

            ) pans

            GROUP BY pan

            ORDER BY
                total_alerts DESC,
                pan

            LIMIT %s
            """,
            (limit,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()

def get_top_isins(
    connection: PGConnection,
    limit=10
):

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT

                isin_code,
                COUNT(*) AS total_alerts

            FROM vw_alert_summary

            WHERE
                isin_code IS NOT NULL
                AND BTRIM(isin_code) <> ''
                AND LOWER(BTRIM(isin_code)) NOT IN ('nan', 'none', 'null')

            GROUP BY isin_code

            ORDER BY
                total_alerts DESC,
                isin_code

            LIMIT %s
            """,
            (limit,)
        )

        return cursor.fetchall()

    finally:

        cursor.close()


def get_city_heatmap(
    connection: PGConnection,
    limit=20
):
    cursor = connection.cursor()
    
    try:
    
            cursor.execute(
                """
                    WITH top_cities AS
                (
                    SELECT
                        city,
                        COUNT(*) AS total_alerts
                    FROM
                    (
                        SELECT source_city AS city
                        FROM vw_alert_summary
                        WHERE source_city IS NOT NULL
                            AND BTRIM(source_city) <> ''
                            AND LOWER(BTRIM(source_city)) NOT IN ('nan', 'none', 'null')

                        UNION ALL

                        SELECT target_city AS city
                        FROM vw_alert_summary
                        WHERE target_city IS NOT NULL
                            AND BTRIM(target_city) <> ''
                            AND LOWER(BTRIM(target_city)) NOT IN ('nan', 'none', 'null')
                    ) c

                    GROUP BY city
                    ORDER BY total_alerts DESC
                    LIMIT %s
                )

                SELECT

                    x.city,
                    x.report_year,
                    x.report_month,
                    COUNT(*) AS alerts

                FROM
                (
                    SELECT
                        source_city AS city,
                        report_year,
                        report_month
                    FROM vw_alert_summary
                    WHERE source_city IS NOT NULL
                        AND BTRIM(source_city) <> ''
                        AND LOWER(BTRIM(source_city)) NOT IN ('nan', 'none', 'null')

                    UNION ALL

                    SELECT
                        target_city,
                        report_year,
                        report_month
                    FROM vw_alert_summary
                    WHERE target_city IS NOT NULL
                        AND BTRIM(target_city) <> ''
                        AND LOWER(BTRIM(target_city)) NOT IN ('nan', 'none', 'null')
                ) x

                JOIN top_cities tc
                ON x.city = tc.city

                GROUP BY

                    x.city,
                    x.report_year,
                    x.report_month

                ORDER BY

                    x.city,
                    x.report_year,
                    x.report_month;
            """,
            (limit,)
        )
            
            return cursor.fetchall()
            
    finally:
            
            cursor.close()

def get_kpi_cards(
    connection: PGConnection
):
    cursor = connection.cursor()
    
    try:
    
            cursor.execute(
                """
                    SELECT
                (
                    SELECT COUNT(*)
                    FROM vw_alert_summary
                ) AS total_alerts,

                (
                    SELECT COUNT(DISTINCT pan)
                    FROM
                    (
                        SELECT source_pan AS pan
                        FROM vw_alert_summary
                        WHERE source_pan IS NOT NULL
                            AND BTRIM(source_pan) <> ''
                            AND LOWER(BTRIM(source_pan)) NOT IN ('nan', 'none', 'null')

                        UNION

                        SELECT target_pan
                        FROM vw_alert_summary
                        WHERE target_pan IS NOT NULL
                            AND BTRIM(target_pan) <> ''
                            AND LOWER(BTRIM(target_pan)) NOT IN ('nan', 'none', 'null')
                    ) p
                ) AS total_pans,

                (
                    
                    SELECT COUNT(DISTINCT isin_code)
                        FROM vw_alert_summary
                        WHERE isin_code IS NOT NULL
                            AND BTRIM(isin_code) <> ''
                            AND LOWER(BTRIM(isin_code)) NOT IN ('nan', 'none', 'null')
                    ) AS total_isins,

                (
                    SELECT COUNT(DISTINCT city)
                    FROM
                    (
                        SELECT source_city AS city
                        FROM vw_alert_summary
                        WHERE source_city IS NOT NULL
                            AND BTRIM(source_city) <> ''
                            AND LOWER(BTRIM(source_city)) NOT IN ('nan', 'none', 'null')

                        UNION

                        SELECT target_city
                        FROM vw_alert_summary
                        WHERE target_city IS NOT NULL
                            AND BTRIM(target_city) <> ''
                            AND LOWER(BTRIM(target_city)) NOT IN ('nan', 'none', 'null')
                    ) c
                ) AS total_cities;

            """
            )
            
            return cursor.fetchone()
            
    finally:
            
            cursor.close()