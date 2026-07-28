"""
database_service.py

Coordinates FIU database browsing.
"""
import pandas as pd
from backend.database.db_connection import (
    get_connection
)

from backend.repositories.database_repository import (
    get_database_records,
    get_database_count,
    get_pan_database_report,
    get_isin_database_report
)



def browse_database(

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
    connection = None

    try:

            connection = get_connection()

            total_records = get_database_count(

                connection,

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

            transaction_rows = get_database_records(
                connection,

                page=page,
                page_size=page_size,
                paginate=True,

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


            # ---------------------------------------------------------
            # PAN REPORT - PostgreSQL aggregation
            # ---------------------------------------------------------

            pan_rows = get_pan_database_report(

                connection,

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

            pan_report = pd.DataFrame(
                pan_rows,
                columns=[
                    "PAN",
                    "Name",
                    "Total Alerts",
                    "FIU Alerts"
                ]
            )


          
            # ---------------------------------------------------------
            # ISIN REPORT - PostgreSQL aggregation
            # ---------------------------------------------------------

            isin_rows = get_isin_database_report(

                connection,

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

            isin_report = pd.DataFrame(
                isin_rows,
                columns=[
                    "ISIN",
                    "Security",
                    "Total Alerts",
                    "FIU Alerts"
                ]
            )
            
            return {

                "total_records": total_records,

                "page": page,

                "page_size": page_size,

                "records": transaction_rows,

                "pan_report": pan_report,

                "isin_report": isin_report

            }

    finally:

            if connection:
                connection.close()