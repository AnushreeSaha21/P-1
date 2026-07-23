"""
database_repository.py

Handles database browsing operations.
"""

from psycopg2.extensions import connection as PGConnection

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

        params = []

        if report_year:

            query += """
                AND report_year = %s
            """

            params.append(report_year)

        if report_month:

            query += """
                AND report_month = %s
            """

            params.append(report_month)

        if report_fortnight:

            query += """
                AND report_fortnight = %s
            """

            params.append(report_fortnight)

        if fiu_alert_type:

            query += """
                AND fiu_alert_type = %s
            """

            params.append(fiu_alert_type)

        if source_system:

            query += """
                AND source_system = %s
            """

            params.append(source_system)

        if source_pan:

            query += """
                AND source_pan ILIKE %s
            """

            params.append(f"%{source_pan}%")

        if target_pan:

            query += """
                AND target_pan ILIKE %s
            """

            params.append(f"%{target_pan}%")

        if source_name:

            query += """
                AND source_name ILIKE %s
            """

            params.append(f"%{source_name}%")

        if target_name:

            query += """
                AND target_name ILIKE %s
            """

            params.append(f"%{target_name}%")

        if source_dp_id:

            query += """
                AND source_dp_id ILIKE %s
            """

            params.append(f"%{source_dp_id}%")

        if source_client_id:

            query += """
                AND source_client_id ILIKE %s
            """

            params.append(f"%{source_client_id}%")

        if target_dp_id:

            query += """
                AND target_dp_id ILIKE %s
            """

            params.append(f"%{target_dp_id}%")

        if target_client_id:

            query += """
                AND target_client_id ILIKE %s
            """

            params.append(f"%{target_client_id}%")

        if transaction_indicator:

            query += """
                AND transaction_indicator = %s
            """

            params.append(transaction_indicator)

        if isin_code:

            query += """
                AND isin_code ILIKE %s
            """

            params.append(f"%{isin_code}%")
        
        if isin_name:

            query += """
                AND isin_name ILIKE %s
            """

            params.append(f"%{isin_name}%")


        if paginate:

            offset = (page - 1) * page_size

            query += """
            ORDER BY
                report_year DESC,
                report_month DESC,
                report_fortnight DESC
            LIMIT %s
            OFFSET %s
            """

            params.extend(
                [
                    page_size,
                    offset
                ]
            )

        else:

            query += """
            ORDER BY
                report_year DESC,
                report_month DESC,
                report_fortnight DESC
            """

        cursor.execute(
                    query,
                    tuple(params)
                )

        rows = cursor.fetchall()

        return rows

    finally: 
        cursor.close()

def get_pan_database_report_rows(
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
):
    
    cursor = connection.cursor()

    try:

        query = """
            SELECT
                source_pan,
                source_name,
                target_pan,
                target_name,

                file_id,

                fiu_alert_type,

                report_year,
                report_month,
                report_fortnight
            FROM vw_alert_summary
            WHERE 1=1
        """

        params = []

        if report_year:

            query += """
                AND report_year = %s
            """

            params.append(report_year)

        if report_month:

            query += """
                AND report_month = %s
            """

            params.append(report_month)

        if report_fortnight:

            query += """
                AND report_fortnight = %s
            """

            params.append(report_fortnight)

        if fiu_alert_type:

            query += """
                AND fiu_alert_type = %s
            """

            params.append(fiu_alert_type)

        if source_system:

            query += """
                AND source_system = %s
            """

            params.append(source_system)

        if source_pan:

            query += """
                AND source_pan ILIKE %s
            """

            params.append(f"%{source_pan}%")

        if target_pan:

            query += """
                AND target_pan ILIKE %s
            """

            params.append(f"%{target_pan}%")

        if source_name:

            query += """
                AND source_name ILIKE %s
            """

            params.append(f"%{source_name}%")

        if target_name:

            query += """
                AND target_name ILIKE %s
            """

            params.append(f"%{target_name}%")

        if source_dp_id:

            query += """
                AND source_dp_id ILIKE %s
            """

            params.append(f"%{source_dp_id}%")

        if source_client_id:

            query += """
                AND source_client_id ILIKE %s
            """

            params.append(f"%{source_client_id}%")

        if target_dp_id:

            query += """
                AND target_dp_id ILIKE %s
            """

            params.append(f"%{target_dp_id}%")

        if target_client_id:

            query += """
                AND target_client_id ILIKE %s
            """

            params.append(f"%{target_client_id}%")

        if transaction_indicator:

            query += """
                AND transaction_indicator = %s
            """

            params.append(transaction_indicator)

        

        query += """
            ORDER BY
                report_year,
                report_month,
                report_fortnight
            """

        

        cursor.execute(
            query,
            tuple(params)
        )

        rows = cursor.fetchall()

        return rows

    finally: 
        cursor.close()




def get_database_count(
        connection: PGConnection,

    page=1,
    page_size=100,

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

        params = []

        if report_year:

            query += """
                AND report_year = %s
            """

            params.append(report_year)

        if report_month:

            query += """
                AND report_month = %s
            """

            params.append(report_month)

        if report_fortnight:

            query += """
                AND report_fortnight = %s
            """

            params.append(report_fortnight)

        if fiu_alert_type:

            query += """
                AND fiu_alert_type = %s
            """

            params.append(fiu_alert_type)

        if source_system:

            query += """
                AND source_system = %s
            """

            params.append(source_system)

        if source_pan:

            query += """
                AND source_pan ILIKE %s
            """

            params.append(f"%{source_pan}%")

        if target_pan:

            query += """
                AND target_pan ILIKE %s
            """

            params.append(f"%{target_pan}%")

        if source_name:

            query += """
                AND source_name ILIKE %s
            """

            params.append(f"%{source_name}%")

        if target_name:

            query += """
                AND target_name ILIKE %s
            """

            params.append(f"%{target_name}%")

        if source_dp_id:

            query += """
                AND source_dp_id ILIKE %s
            """

            params.append(f"%{source_dp_id}%")

        if source_client_id:

            query += """
                AND source_client_id ILIKE %s
            """

            params.append(f"%{source_client_id}%")

        if target_dp_id:

            query += """
                AND target_dp_id ILIKE %s
            """

            params.append(f"%{target_dp_id}%")

        if target_client_id:

            query += """
                AND target_client_id ILIKE %s
            """

            params.append(f"%{target_client_id}%")

        if transaction_indicator:

            query += """
                AND transaction_indicator = %s
            """

            params.append(transaction_indicator)

        if isin_code:

            query += """
                AND isin_code ILIKE %s
            """

            params.append(f"%{isin_code}%")
        
        if isin_name:

            query += """
                AND isin_name ILIKE %s
            """

            params.append(f"%{isin_name}%")


        cursor.execute(
            query,
            tuple(params)
        )


        return cursor.fetchone()[0]

    finally: 
        cursor.close()



