
"""
filename_parser.py

Parses FIU Excel filenames and extracts metadata such as:
- Source System (CDSL / NSDL)
- FIU Alert Type
- Transaction Type
- Reporting Period
"""

import os
import re
import calendar
from datetime import date

from backend.utils.constants import *


# ----------------------------------------------------------
# Public Function
# ----------------------------------------------------------

def parse_filename(filename: str) -> dict:
    """
    Detects whether the file belongs to CDSL or NSDL
    and parses accordingly.
    """

    filename = os.path.basename(filename)
    filename = os.path.splitext(filename)[0]

    if filename.lower().startswith("fiu"):
        if "_" == filename[3]:
            return _parse_nsdl(filename)
        else:
            return _parse_cdsl(filename)

    raise ValueError(f"Invalid FIU filename : {filename}")


# ----------------------------------------------------------
# CDSL
# ----------------------------------------------------------

def _parse_cdsl(filename: str) -> dict:
    """
    Example:

    fiu1_drcr_sum_150426
    fiu2_pledge_txns_300426
    fiu3_drcr_avg_sum_150426
    fiu4_offmkt_sum_300426
    """

    pattern = (
        r"^fiu"
        r"(?P<fiu>[1-5])_"
        r"(?P<transaction>[a-z_]+)_"
        r"(?P<date>\d{6})$"
    )

    match = re.match(pattern, filename, re.IGNORECASE)

    if not match:
        raise ValueError(f"Invalid CDSL filename : {filename}")

    fiu_type = int(match.group("fiu"))

    transaction = match.group("transaction").lower()

    end_date = match.group("date")

    day = int(end_date[:2])
    month = int(end_date[2:4])
    year = 2000 + int(end_date[4:])

    report_fortnight = FIRST_FORTNIGHT if day == 15 else SECOND_FORTNIGHT

    if report_fortnight == FIRST_FORTNIGHT:
        start_day = 1
    else:
        start_day = 16

    transaction_mapping = {
        "drcr_sum": DRCR_SUM,
        "drcr_avg_sum": DRCR_AVG_SUM,
        "pledge_txns": PLEDGE,
        "offmkt_sum": OFF_MARKET,
    }

    transaction_type = transaction_mapping.get(
        transaction,
        transaction.upper()
    )

    return {

        "file_name": filename.lower(),          
        "original_file_name": filename,
        "source_system": CDSL,

        "fiu_alert_type": fiu_type,

        "transaction_type": transaction_type,

        "report_year": year,

        "report_month": month,

        "report_fortnight": report_fortnight,

        "fortnight_start": date(year, month, start_day),

        "fortnight_end": date(year, month, day)

    }


# ----------------------------------------------------------
# NSDL
# ----------------------------------------------------------

def _parse_nsdl(filename: str) -> dict:
    """
    Example:

    FIU_1_16Apr26
    FIU_5_30Apr26
    """

    pattern = (
        r"^FIU_"
        r"(?P<fiu>[1-5])_"
        r"(?P<day>\d{2})"
        r"(?P<month>[A-Za-z]{3})"
        r"(?P<year>\d{2})$"
    )

    match = re.match(pattern, filename, re.IGNORECASE)

    if not match:
        raise ValueError(f"Invalid NSDL filename : {filename}")

    fiu_type = int(match.group("fiu"))

    day = int(match.group("day"))

    month_name = match.group("month").title()

    month = list(calendar.month_abbr).index(month_name)

    year = 2000 + int(match.group("year"))

    last_day = calendar.monthrange(year, month)[1]

    if day <= 16:
        report_fortnight = FIRST_FORTNIGHT
        start_day = 1
    else:
        report_fortnight = SECOND_FORTNIGHT
        start_day = 17

    return {

        "file_name": filename.lower(),          
        "original_file_name": filename,
        "source_system": NSDL,

        "fiu_alert_type": fiu_type,

        "transaction_type": None,

        "report_year": year,

        "report_month": month,

        "report_fortnight": report_fortnight,

        "fortnight_start": date(year, month, start_day),

        "fortnight_end": date(year, month, min(day, last_day))

    }

