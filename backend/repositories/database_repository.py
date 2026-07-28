"""
database_repository.py

Handles database browsing operations.
"""

from psycopg2.extensions import connection as PGConnection

def _build_database_filters(
    report_year=None,
    report_month=None,
    report_fortnight=None,

    fiu_alert_type=None,
    source_system=None,

    source_dp_id=None,
    source_client_id=None,
    source_pan=None,
    source_name=None,

    target_dp_id=None,
    target_client_id=None,
    target_pan=None,
    target_name=None,

    transaction_indicator=None,

    isin_code=None,
    isin_name=None
):
    """
    Builds the common WHERE conditions used by database searches.

    Exact-match fields:
        PAN, DP ID, BO/Client ID, ISIN, reporting metadata.

    Partial-match fields:
        Source Name, Target Name, Security Name.
    """

    conditions = []
    params = []

    # ---------------------------------------------------------
    # Reporting metadata
    # ---------------------------------------------------------

    if report_year:
        conditions.append("report_year = %s")
        params.append(report_year)

    if report_month:
        conditions.append("report_month = %s")
        params.append(report_month)

    if report_fortnight:
        conditions.append("report_fortnight = %s")
        params.append(report_fortnight)

    if fiu_alert_type:
        conditions.append("fiu_alert_type = %s")
        params.append(fiu_alert_type)

    if source_system:
        conditions.append("source_system = %s")
        params.append(source_system)

    # ---------------------------------------------------------
    # Source
    # ---------------------------------------------------------

    if source_dp_id:
        conditions.append("source_dp_id = %s")
        params.append(source_dp_id.strip())

    if source_client_id:
        conditions.append("source_client_id = %s")
        params.append(source_client_id.strip())

    if source_pan:
        conditions.append("source_pan = %s")
        params.append(source_pan.strip().upper())

    if source_name:
        conditions.append("source_name ILIKE %s")
        params.append(f"%{source_name.strip()}%")

    # ---------------------------------------------------------
    # Target
    # ---------------------------------------------------------

    if target_dp_id:
        conditions.append("target_dp_id = %s")
        params.append(target_dp_id.strip())

    if target_client_id:
        conditions.append("target_client_id = %s")
        params.append(target_client_id.strip())

    if target_pan:
        conditions.append("target_pan = %s")
        params.append(target_pan.strip().upper())

    if target_name:
        conditions.append("target_name ILIKE %s")
        params.append(f"%{target_name.strip()}%")

    # ---------------------------------------------------------
    # Transaction
    # ---------------------------------------------------------

    if transaction_indicator:
        conditions.append("transaction_indicator = %s")
        params.append(transaction_indicator)

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    if isin_code:
        conditions.append("isin_code = %s")
        params.append(isin_code.strip().upper())

    if isin_name:
        conditions.append("isin_name ILIKE %s")
        params.append(f"%{isin_name.strip()}%")

    if conditions:
        where_clause = " AND " + " AND ".join(conditions)
    else:
        where_clause = ""

    return where_clause, params


def get_database_records(
    connection: PGConnection,

    page=1,
    page_size=100,
    paginate=True,

    report_year=None,
    report_month=None,
    report_fortnight=None,

    fiu_alert_type=None,
    source_system=None,

    source_dp_id=None,
    source_client_id=None,
    source_pan=None,
    source_name=None,

    target_dp_id=None,
    target_client_id=None,
    target_pan=None,
    target_name=None,

    transaction_indicator=None,

    isin_code=None,
    isin_name=None
):

    cursor = connection.cursor()

    try:

        query = """
            SELECT
                report_year,
                report_month,
                report_fortnight,

                source_system,
                fiu_alert_type,

                source_dp_id,
                source_client_id,
                source_pan,
                source_name,

                target_dp_id,
                target_client_id,
                target_pan,
                target_name,

                transaction_indicator,
                transaction_type,

                isin_code,
                isin_name,

                quantity,
                valuation

            FROM vw_alert_summary
            WHERE 1=1
        """

        where_clause, params = _build_database_filters(

            report_year=report_year,
            report_month=report_month,
            report_fortnight=report_fortnight,

            fiu_alert_type=fiu_alert_type,
            source_system=source_system,

            source_dp_id=source_dp_id,
            source_client_id=source_client_id,
            source_pan=source_pan,
            source_name=source_name,

            target_dp_id=target_dp_id,
            target_client_id=target_client_id,
            target_pan=target_pan,
            target_name=target_name,

            transaction_indicator=transaction_indicator,

            isin_code=isin_code,
            isin_name=isin_name
        )

        query += where_clause

        query += """
            ORDER BY
                report_year DESC,
                report_month DESC,
                report_fortnight DESC
        """

        if paginate:

            offset = (page - 1) * page_size

            query += """
                LIMIT %s
                OFFSET %s
            """

            params.extend([
                page_size,
                offset
            ])

        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:
        cursor.close()

def get_database_count(
    connection: PGConnection,

    report_year=None,
    report_month=None,
    report_fortnight=None,

    fiu_alert_type=None,
    source_system=None,

    source_dp_id=None,
    source_client_id=None,
    source_pan=None,
    source_name=None,

    target_dp_id=None,
    target_client_id=None,
    target_pan=None,
    target_name=None,

    transaction_indicator=None,

    isin_code=None,
    isin_name=None
):

    cursor = connection.cursor()

    try:

        query = """
            SELECT COUNT(*)
            FROM vw_alert_summary
            WHERE 1=1
        """

        where_clause, params = _build_database_filters(

            report_year=report_year,
            report_month=report_month,
            report_fortnight=report_fortnight,

            fiu_alert_type=fiu_alert_type,
            source_system=source_system,

            source_dp_id=source_dp_id,
            source_client_id=source_client_id,
            source_pan=source_pan,
            source_name=source_name,

            target_dp_id=target_dp_id,
            target_client_id=target_client_id,
            target_pan=target_pan,
            target_name=target_name,

            transaction_indicator=transaction_indicator,

            isin_code=isin_code,
            isin_name=isin_name
        )

        query += where_clause

        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchone()[0]

    finally:
        cursor.close()

def get_pan_database_report(
    connection: PGConnection,

    report_year=None,
    report_month=None,
    report_fortnight=None,

    fiu_alert_type=None,
    source_system=None,

    source_dp_id=None,
    source_client_id=None,
    source_pan=None,
    source_name=None,

    target_dp_id=None,
    target_client_id=None,
    target_pan=None,
    target_name=None,

    transaction_indicator=None,

    isin_code=None,
    isin_name=None
):

    cursor = connection.cursor()

    try:
        where_clause, params = _build_database_filters(

            report_year=report_year,
            report_month=report_month,
            report_fortnight=report_fortnight,

            fiu_alert_type=fiu_alert_type,
            source_system=source_system,

            source_dp_id=source_dp_id,
            source_client_id=source_client_id,
            source_pan=source_pan,
            source_name=source_name,

            target_dp_id=target_dp_id,
            target_client_id=target_client_id,
            target_pan=target_pan,
            target_name=target_name,

            transaction_indicator=transaction_indicator,

            isin_code=isin_code,
            isin_name=isin_name
        )

        query = f"""
            WITH filtered AS (
                SELECT
                    source_pan,
                    source_name,
                    target_pan,
                    target_name,
                    fiu_alert_type,
                    report_year,
                    report_month,
                    report_fortnight

                FROM vw_alert_summary
                WHERE 1=1
                {where_clause}
            ),

            pan_occurrences AS (

                SELECT
                    source_pan AS pan,
                    source_name AS name,
                    fiu_alert_type,
                    report_year,
                    report_month,
                    report_fortnight
                FROM filtered
                WHERE
                    source_pan IS NOT NULL
                    AND BTRIM(source_pan) <> ''

                UNION ALL

                SELECT
                    target_pan AS pan,
                    target_name AS name,
                    fiu_alert_type,
                    report_year,
                    report_month,
                    report_fortnight
                FROM filtered
                WHERE
                    target_pan IS NOT NULL
                    AND BTRIM(target_pan) <> ''
            ),

            alert_groups AS (
                SELECT
                    pan,
                    fiu_alert_type,
                    report_year,
                    report_month,
                    report_fortnight,
                    COUNT(*) AS transaction_count

                FROM pan_occurrences

                GROUP BY
                    pan,
                    fiu_alert_type,
                    report_year,
                    report_month,
                    report_fortnight
            ),

            pan_names AS (
                SELECT
                    pan,
                    MAX(name) FILTER (
                        WHERE name IS NOT NULL
                        AND BTRIM(name) <> ''
                    ) AS name

                FROM pan_occurrences

                GROUP BY pan
            ),

            pan_totals AS (
                SELECT
                    pan,
                    COUNT(*) AS total_alerts

                FROM pan_occurrences

                GROUP BY pan
            )

            SELECT
                t.pan,
                n.name,
                t.total_alerts,

                STRING_AGG(
                    CONCAT(
                        'FIU-',
                        a.fiu_alert_type,
                        ' (',
                        CASE
                            WHEN a.report_fortnight = 1
                                THEN '1st Fortnight'
                            ELSE '2nd Fortnight'
                        END,
                        ', ',
                        TO_CHAR(
                            MAKE_DATE(
                                a.report_year,
                                a.report_month,
                                1
                            ),
                            'Mon YYYY'
                        ),
                        ')',
                        CASE
                            WHEN a.transaction_count > 1
                            THEN CONCAT(
                                ' [',
                                a.transaction_count,
                                ' Transactions]'
                            )
                            ELSE ''
                        END
                    ),
                    E'\\n'
                    ORDER BY
                        a.report_year,
                        a.report_month,
                        a.report_fortnight,
                        a.fiu_alert_type
                ) AS fiu_alerts

            FROM pan_totals t

            JOIN alert_groups a
                ON a.pan = t.pan

            LEFT JOIN pan_names n
                ON n.pan = t.pan

            GROUP BY
                t.pan,
                n.name,
                t.total_alerts

            ORDER BY
                t.total_alerts DESC,
                t.pan
        """

        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:
        cursor.close()

def get_isin_database_report(
    connection: PGConnection,

    report_year=None,
    report_month=None,
    report_fortnight=None,

    fiu_alert_type=None,
    source_system=None,

    source_dp_id=None,
    source_client_id=None,
    source_pan=None,
    source_name=None,

    target_dp_id=None,
    target_client_id=None,
    target_pan=None,
    target_name=None,

    transaction_indicator=None,

    isin_code=None,
    isin_name=None
):

    cursor = connection.cursor()

    try:

        where_clause, params = _build_database_filters(

            report_year=report_year,
            report_month=report_month,
            report_fortnight=report_fortnight,

            fiu_alert_type=fiu_alert_type,
            source_system=source_system,

            source_dp_id=source_dp_id,
            source_client_id=source_client_id,
            source_pan=source_pan,
            source_name=source_name,

            target_dp_id=target_dp_id,
            target_client_id=target_client_id,
            target_pan=target_pan,
            target_name=target_name,

            transaction_indicator=transaction_indicator,

            isin_code=isin_code,
            isin_name=isin_name
        )

        query = f"""
            WITH filtered AS (
                SELECT
                    isin_code,
                    isin_name,
                    fiu_alert_type,
                    report_year,
                    report_month,
                    report_fortnight

                FROM vw_alert_summary
                WHERE 1=1
                {where_clause}

                AND isin_code IS NOT NULL
                AND BTRIM(isin_code) <> ''
            ),

            alert_groups AS (
                SELECT
                    isin_code,
                    fiu_alert_type,
                    report_year,
                    report_month,
                    report_fortnight,
                    COUNT(*) AS transaction_count

                FROM filtered

                GROUP BY
                    isin_code,
                    fiu_alert_type,
                    report_year,
                    report_month,
                    report_fortnight
            ),

            isin_details AS (
                SELECT
                    isin_code,

                    MAX(isin_name) FILTER (
                        WHERE isin_name IS NOT NULL
                        AND BTRIM(isin_name) <> ''
                    ) AS isin_name,

                    COUNT(*) AS total_alerts

                FROM filtered

                GROUP BY isin_code
            )

            SELECT
                d.isin_code,
                d.isin_name,
                d.total_alerts,

                STRING_AGG(
                    CONCAT(
                        'FIU-',
                        a.fiu_alert_type,
                        ' (',

                        CASE
                            WHEN a.report_fortnight = 1
                                THEN '1st Fortnight'
                            ELSE '2nd Fortnight'
                        END,

                        ', ',

                        TO_CHAR(
                            MAKE_DATE(
                                a.report_year,
                                a.report_month,
                                1
                            ),
                            'Mon YYYY'
                        ),

                        ')',

                        CASE
                            WHEN a.transaction_count > 1
                            THEN CONCAT(
                                ' [',
                                a.transaction_count,
                                ' Transactions]'
                            )
                            ELSE ''
                        END
                    ),

                    E'\\n'

                    ORDER BY
                        a.report_year,
                        a.report_month,
                        a.report_fortnight,
                        a.fiu_alert_type

                ) AS fiu_alerts

            FROM isin_details d

            JOIN alert_groups a
                ON a.isin_code = d.isin_code

            GROUP BY
                d.isin_code,
                d.isin_name,
                d.total_alerts

            ORDER BY
                d.total_alerts DESC,
                d.isin_code
        """

        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchall()

    finally:
        cursor.close()

# def get_database_records(
#     connection: PGConnection,

#     page=1,
#     page_size=100,
#     paginate=True,

#     report_year=None,
#     report_month=None,
#     report_fortnight=None,

#     fiu_alert_type=None,
#     source_system=None,

#     source_dp_id=None,
#     source_client_id=None,
#     source_pan=None,
#     source_name=None,

#     target_dp_id=None,
#     target_client_id=None,
#     target_pan=None,
#     target_name=None,

#     transaction_indicator=None,

#     isin_code=None,
#     isin_name=None
# ):
    
#     cursor = connection.cursor()

#     try:

#         query = """
#             SELECT
#                 report_year,
#                 report_month,
#                 report_fortnight,

#                 source_system,
#                 fiu_alert_type,

#                 source_dp_id,
#                 source_client_id,
#                 source_pan,
#                 source_name,

#                 target_dp_id,
#                 target_client_id,
#                 target_pan,
#                 target_name,

#                 transaction_indicator,
#                 transaction_type,

#                 isin_code,
#                 isin_name,

#                 quantity,
#                 valuation

#             FROM vw_alert_summary
#             WHERE 1=1
#         """

#         params = []

#         if report_year:

#             query += """
#                 AND report_year = %s
#             """

#             params.append(report_year)

#         if report_month:

#             query += """
#                 AND report_month = %s
#             """

#             params.append(report_month)

#         if report_fortnight:

#             query += """
#                 AND report_fortnight = %s
#             """

#             params.append(report_fortnight)

#         if fiu_alert_type:

#             query += """
#                 AND fiu_alert_type = %s
#             """

#             params.append(fiu_alert_type)

#         if source_system:

#             query += """
#                 AND source_system = %s
#             """

#             params.append(source_system)

#         if source_pan:

#             query += """
#                 AND source_pan ILIKE %s
#             """

#             params.append(f"%{source_pan}%")

#         if target_pan:

#             query += """
#                 AND target_pan ILIKE %s
#             """

#             params.append(f"%{target_pan}%")

#         if source_name:

#             query += """
#                 AND source_name ILIKE %s
#             """

#             params.append(f"%{source_name}%")

#         if target_name:

#             query += """
#                 AND target_name ILIKE %s
#             """

#             params.append(f"%{target_name}%")

#         if source_dp_id:

#             query += """
#                 AND source_dp_id ILIKE %s
#             """

#             params.append(f"%{source_dp_id}%")

#         if source_client_id:

#             query += """
#                 AND source_client_id ILIKE %s
#             """

#             params.append(f"%{source_client_id}%")

#         if target_dp_id:

#             query += """
#                 AND target_dp_id ILIKE %s
#             """

#             params.append(f"%{target_dp_id}%")

#         if target_client_id:

#             query += """
#                 AND target_client_id ILIKE %s
#             """

#             params.append(f"%{target_client_id}%")

#         if transaction_indicator:

#             query += """
#                 AND transaction_indicator = %s
#             """

#             params.append(transaction_indicator)

#         if isin_code:

#             query += """
#                 AND isin_code ILIKE %s
#             """

#             params.append(f"%{isin_code}%")
        
#         if isin_name:

#             query += """
#                 AND isin_name ILIKE %s
#             """

#             params.append(f"%{isin_name}%")


#         if paginate:

#             offset = (page - 1) * page_size

#             query += """
#             ORDER BY
#                 report_year DESC,
#                 report_month DESC,
#                 report_fortnight DESC
#             LIMIT %s
#             OFFSET %s
#             """

#             params.extend(
#                 [
#                     page_size,
#                     offset
#                 ]
#             )

#         else:

#             query += """
#             ORDER BY
#                 report_year DESC,
#                 report_month DESC,
#                 report_fortnight DESC
#             """

#         cursor.execute(
#                     query,
#                     tuple(params)
#                 )

#         rows = cursor.fetchall()

#         return rows

#     finally: 
#         cursor.close()

# def get_pan_database_report_rows(
#         connection: PGConnection,

#     report_year=None,
#     report_month=None,
#     report_fortnight=None,

#     fiu_alert_type=None,
#     source_system=None,

#     source_dp_id=None,
#     source_client_id=None,
#     source_pan=None,
#     source_name=None,

#     target_dp_id=None,
#     target_client_id=None,
#     target_pan=None,
#     target_name=None,

#     transaction_indicator=None,
# ):
    
#     cursor = connection.cursor()

#     try:

#         query = """
#             SELECT
#                 source_pan,
#                 source_name,
#                 target_pan,
#                 target_name,

#                 file_id,

#                 fiu_alert_type,

#                 report_year,
#                 report_month,
#                 report_fortnight
#             FROM vw_alert_summary
#             WHERE 1=1
#         """

#         params = []

#         if report_year:

#             query += """
#                 AND report_year = %s
#             """

#             params.append(report_year)

#         if report_month:

#             query += """
#                 AND report_month = %s
#             """

#             params.append(report_month)

#         if report_fortnight:

#             query += """
#                 AND report_fortnight = %s
#             """

#             params.append(report_fortnight)

#         if fiu_alert_type:

#             query += """
#                 AND fiu_alert_type = %s
#             """

#             params.append(fiu_alert_type)

#         if source_system:

#             query += """
#                 AND source_system = %s
#             """

#             params.append(source_system)

#         if source_pan:

#             query += """
#                 AND source_pan ILIKE %s
#             """

#             params.append(f"%{source_pan}%")

#         if target_pan:

#             query += """
#                 AND target_pan ILIKE %s
#             """

#             params.append(f"%{target_pan}%")

#         if source_name:

#             query += """
#                 AND source_name ILIKE %s
#             """

#             params.append(f"%{source_name}%")

#         if target_name:

#             query += """
#                 AND target_name ILIKE %s
#             """

#             params.append(f"%{target_name}%")

#         if source_dp_id:

#             query += """
#                 AND source_dp_id ILIKE %s
#             """

#             params.append(f"%{source_dp_id}%")

#         if source_client_id:

#             query += """
#                 AND source_client_id ILIKE %s
#             """

#             params.append(f"%{source_client_id}%")

#         if target_dp_id:

#             query += """
#                 AND target_dp_id ILIKE %s
#             """

#             params.append(f"%{target_dp_id}%")

#         if target_client_id:

#             query += """
#                 AND target_client_id ILIKE %s
#             """

#             params.append(f"%{target_client_id}%")

#         if transaction_indicator:

#             query += """
#                 AND transaction_indicator = %s
#             """

#             params.append(transaction_indicator)

        

#         query += """
#             ORDER BY
#                 report_year,
#                 report_month,
#                 report_fortnight
#             """

        

#         cursor.execute(
#             query,
#             tuple(params)
#         )

#         rows = cursor.fetchall()

#         return rows

#     finally: 
#         cursor.close()

# def get_database_count(
#         connection: PGConnection,

#     page=1,
#     page_size=100,

#     report_year=None,
#     report_month=None,
#     report_fortnight=None,

#     fiu_alert_type=None,
#     source_system=None,

#     source_dp_id=None,
#     source_client_id=None,
#     source_pan=None,
#     source_name=None,

#     target_dp_id=None,
#     target_client_id=None,
#     target_pan=None,
#     target_name=None,

#     transaction_indicator=None,

#     isin_code=None,
#     isin_name=None
# ):
    
#     cursor = connection.cursor()

#     try:

#         query = """
#             SELECT COUNT(*)
#             FROM vw_alert_summary
#             WHERE 1=1
#         """

#         params = []

#         if report_year:

#             query += """
#                 AND report_year = %s
#             """

#             params.append(report_year)

#         if report_month:

#             query += """
#                 AND report_month = %s
#             """

#             params.append(report_month)

#         if report_fortnight:

#             query += """
#                 AND report_fortnight = %s
#             """

#             params.append(report_fortnight)

#         if fiu_alert_type:

#             query += """
#                 AND fiu_alert_type = %s
#             """

#             params.append(fiu_alert_type)

#         if source_system:

#             query += """
#                 AND source_system = %s
#             """

#             params.append(source_system)

#         if source_pan:

#             query += """
#                 AND source_pan ILIKE %s
#             """

#             params.append(f"%{source_pan}%")

#         if target_pan:

#             query += """
#                 AND target_pan ILIKE %s
#             """

#             params.append(f"%{target_pan}%")

#         if source_name:

#             query += """
#                 AND source_name ILIKE %s
#             """

#             params.append(f"%{source_name}%")

#         if target_name:

#             query += """
#                 AND target_name ILIKE %s
#             """

#             params.append(f"%{target_name}%")

#         if source_dp_id:

#             query += """
#                 AND source_dp_id ILIKE %s
#             """

#             params.append(f"%{source_dp_id}%")

#         if source_client_id:

#             query += """
#                 AND source_client_id ILIKE %s
#             """

#             params.append(f"%{source_client_id}%")

#         if target_dp_id:

#             query += """
#                 AND target_dp_id ILIKE %s
#             """

#             params.append(f"%{target_dp_id}%")

#         if target_client_id:

#             query += """
#                 AND target_client_id ILIKE %s
#             """

#             params.append(f"%{target_client_id}%")

#         if transaction_indicator:

#             query += """
#                 AND transaction_indicator = %s
#             """

#             params.append(transaction_indicator)

#         if isin_code:

#             query += """
#                 AND isin_code ILIKE %s
#             """

#             params.append(f"%{isin_code}%")
        
#         if isin_name:

#             query += """
#                 AND isin_name ILIKE %s
#             """

#             params.append(f"%{isin_name}%")


#         cursor.execute(
#             query,
#             tuple(params)
#         )


#         return cursor.fetchone()[0]

#     finally: 
#         cursor.close()



