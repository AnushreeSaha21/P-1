"""
excel_reader.py

Responsible only for reading Excel files.
Returns a Pandas DataFrame.
"""
import os

from io import BytesIO
from pathlib import Path

import pandas as pd
import msoffcrypto


class ExcelReaderError(Exception):
    """Base exception for Excel Reader."""
    pass


class InvalidPasswordError(ExcelReaderError):
    """Raised when an incorrect password is supplied."""
    pass


class UnsupportedFileError(ExcelReaderError):
    """Raised when file type is unsupported."""
    pass


def read_excel(file_path: str, password: str | None = None) -> pd.DataFrame:
    """
    Reads password protected and non-password protected
    Excel files and returns a Pandas DataFrame.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(file_path)

    extension = path.suffix.lower()

    if extension not in [".xls", ".xlsx"]:
        raise UnsupportedFileError(
            f"Unsupported file type: {extension}"
        )

    # ------------------------------------
    # Normal Excel
    # ------------------------------------

    if password is None:
        return pd.read_excel(path)

    # ------------------------------------
    # Password Protected Excel
    # ------------------------------------

    decrypted = BytesIO()

    try:

        with open(path, "rb") as file:

            office_file = msoffcrypto.OfficeFile(file)

            office_file.load_key(password=password)

            office_file.decrypt(decrypted)

    except Exception as e:

        raise InvalidPasswordError(
            "Incorrect password or corrupted file."
        ) from e

    decrypted.seek(0)

    return pd.read_excel(decrypted)

