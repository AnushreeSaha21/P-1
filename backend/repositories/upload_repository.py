"""
upload_repository.py

Handles all database operations related to
FIU file uploads.
"""
import pandas as pd
from psycopg2.extras import execute_values

from psycopg2.extensions import connection as PGConnection

def file_exists(
    connection: PGConnection,
    file_name: str
) -> bool:
    """
    Returns True if the file has already been uploaded.
    """
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM uploaded_files
                WHERE file_name = %s
            )
            """,
            (file_name,)
        )

        return cursor.fetchone()[0]

    finally:

        cursor.close()
       




def insert_uploaded_file(
    connection: PGConnection,
    metadata: dict
) -> int:
    """
    Inserts one record into uploaded_files.

    Returns
    -------
    int
        Newly created file_id.
    """

    
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
           INSERT INTO uploaded_files
            (
                file_name,
                original_file_name,
                source_system,
                fiu_alert_type,
                report_year,
                report_month,
                report_fortnight,
                fortnight_start,
                fortnight_end,
                total_records
            )

            VALUES
            (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )

            RETURNING file_id
            """,

            (
                
                    metadata["file_name"],
                    metadata["original_file_name"],
                    metadata["source_system"],
                    metadata["fiu_alert_type"],
                    metadata["report_year"],
                    metadata["report_month"],
                    metadata["report_fortnight"],
                    metadata["fortnight_start"],
                    metadata["fortnight_end"],
                    metadata["total_records"]
                
            )

        )

        file_id = cursor.fetchone()[0]

        return file_id

    except Exception:
        raise

    finally:

        cursor.close()
        


def insert_alerts(
    connection: PGConnection,
    df: pd.DataFrame,
    file_id: int
)-> int:
    """
    Inserts all FIU alerts into fiu_alerts table.
    """

    cursor = connection.cursor()

    try:

        # -----------------------------------
        # Add File ID
        # -----------------------------------

        df = df.copy()

        df.insert(0, "file_id", file_id)
        # print(df[["file_id"]].head())

        # -----------------------------------
        # Convert DataFrame into list of tuples
        # -----------------------------------

        records = list(df.itertuples(index=False, name=None))

        # -----------------------------------
        # Column Names
        # -----------------------------------

        columns = list(df.columns)

        sql = f"""
        INSERT INTO fiu_alerts
        ({",".join(columns)})
        VALUES %s
        """

        # print(records[:3])
        execute_values(
            cursor,
            sql,
            records,
            page_size=1000
        )

        return len(records)

    finally:

        cursor.close()


def get_upload_summary(
    connection: PGConnection,
    file_id: int
):
    """
    Returns the Upload Intelligence Report
    for the uploaded file.
    """
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                alert_pan,
                alert_name,
                file_id,
                fiu_alert_type,
                report_year,
                report_month,
                report_fortnight
            FROM vw_alert_summary
            WHERE
                alert_pan IS NOT NULL
                AND file_id <= %s
            ORDER BY
                alert_pan,
                report_year,
                report_month,
                report_fortnight
            """,
            (file_id,)
        )

        rows = cursor.fetchall()
        return rows

    finally:

        cursor.close()




