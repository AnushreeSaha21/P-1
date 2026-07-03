"""
upload_service.py

Coordinates the complete FIU upload workflow.
"""

class UploadServiceError(Exception):
    """Raised when upload fails."""
    pass

from pathlib import Path

from backend.database.db_connection import get_connection

from backend.parser.excel_reader import read_excel
from backend.parser.filename_parser import parse_filename

from backend.parser.nsdl_parser import parse_nsdl
from backend.parser.cdsl_parser import parse_cdsl

from backend.repositories.upload_repository import (
    file_exists,
    insert_uploaded_file,
    insert_alerts
)

from backend.utils.constants import (
    NSDL,
    CDSL,
    
)

def upload_file(
    file_path: str,
    password: str | None = None
):
    """
    Complete upload workflow.

    Parameters
    ----------
    file_path : str

    password : str | None
    """

    file_name = Path(file_path).name

    connection = None

    try:

        metadata = parse_filename(file_name)

        df = read_excel(file_path, password)

        if metadata["source_system"] == NSDL:
            parsed_df = parse_nsdl(df, metadata)

        elif metadata["source_system"] == CDSL:
            parsed_df = parse_cdsl(df, metadata)

        else:
            raise UploadServiceError("Unsupported depository.")

        metadata["total_records"] = len(parsed_df)

        connection = get_connection()

        if file_exists(connection, metadata["file_name"]):
            raise UploadServiceError("File already uploaded.")
        
        file_id = insert_uploaded_file(connection,metadata)

        rows = insert_alerts(connection,parsed_df,file_id)

        connection.commit()

        return {
            "success": True,
            "file_id": file_id,
            "rows_inserted": rows
        }
    
    except Exception:

        if connection:
            connection.rollback()

        raise

    finally:

        if connection:
            connection.close()