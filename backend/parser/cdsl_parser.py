"""
cdsl_parser.py

Transforms raw CDSL FIU Excel data into the
canonical format used by the FIU Analytics database.
"""

import pandas as pd

from backend.cleaning.cleaner import (
    clean_pan,
    clean_name,
    clean_account_number,
    clean_address,
    clean_city,
    clean_pincode,
    clean_ifsc,
    clean_isin,
    clean_numeric,
    clean_security_name
)

from backend.cleaning.standardizer import (
    standardize_transaction_indicator
)

from backend.utils.constants import (
    DEBIT,
    SOURCE,
    TARGET,
    UNKNOWN,
    FIU_ALERT_COLUMNS
)


# ---------------------------------------------------------
# CDSL COLUMN MAPPING
# ---------------------------------------------------------

COLUMN_MAPPING = {

    # Customer

    "BO-ID": "customer_client_id",
    "CUSTOMER-NAME": "customer_name",
    "PAN-NO": "customer_pan",
    "BANK A/C": "customer_bank_account",
    "BANK NAME": "customer_bank_name",
    "IFSC CODE": "customer_ifsc",
    "CUSTOMER-ADDRESS": "customer_address",
    "CITY": "customer_city",
    "PIN": "customer_pincode",

    # Security

    "ISIN-CODE": "isin_code",
    "ISIN-NAME": "isin_name",

    # Transaction

    "DR/CR": "transaction_indicator",

    # Totals

    "MARKET-TOTAL": "market_total",
    "REMAT-TOTAL": "remat_total",
    "DEMAT-TOTAL": "demat_total",
    "CA-TOTAL": "ca_total",
    "IPO-TOTAL": "ipo_total",
    "CONFIS-TOTAL": "confis_total",
    "GRAND-TOTAL": "grand_total",

    # FIU-2

    "QTY": "quantity",
    "ISIN-RATE": "isin_price",

    # Common

    "ISIN-PRICE": "isin_price",
    "VALUATION": "valuation"
}

def parse_cdsl(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    """
    Main entry point.
    Decides which parser to use.
    """

    if metadata["fiu_alert_type"] == 2:
        return _parse_cdsl_fiu2(df, metadata)

    return _parse_cdsl_standard(df, metadata)


# ---------------------------------------------------------
# FIU-1,3,4,5
# ---------------------------------------------------------

def _parse_cdsl_standard(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    """
    Handles FIU-1, FIU-3, FIU-4 and FIU-5.
    """

    df = df.copy()

    # Normalize columns
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )

    # Rename
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # Cleaning...
    # Standardization...
    
    # Finalize...

    # ---------------------------------------------------------
    # Cleaning
    # ---------------------------------------------------------

    # Customer
    df["customer_pan"] = df["customer_pan"].apply(clean_pan)
    df["customer_name"] = df["customer_name"].apply(clean_name)
    df["customer_bank_account"] = df["customer_bank_account"].apply(clean_account_number)
    df["customer_bank_name"] = df["customer_bank_name"].apply(clean_name)
    df["customer_ifsc"] = df["customer_ifsc"].apply(clean_ifsc)
    df["customer_address"] = df["customer_address"].apply(clean_address)
    df["customer_city"] = df["customer_city"].apply(clean_city)
    df["customer_pincode"] = df["customer_pincode"].apply(clean_pincode)

    # Security
    df["isin_code"] = df["isin_code"].apply(clean_isin)
    df["isin_name"] = df["isin_name"].apply(clean_security_name)

    numeric_cols = [
        "market_total",
        "remat_total",
        "demat_total",
        "ca_total",
        "ipo_total",
        "confis_total",
        "grand_total",
        "isin_price",
        "valuation"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)

    df["transaction_indicator"] = df["transaction_indicator"].apply(
        standardize_transaction_indicator
    )


    # Source/Target logic...

    is_debit = df["transaction_indicator"] == DEBIT

    # Source

    df["source_client_id"] = df["customer_client_id"].where(is_debit)
    df["source_name"] = df["customer_name"].where(is_debit)
    df["source_pan"] = df["customer_pan"].where(is_debit)
    df["source_bank_name"] = df["customer_bank_name"].where(is_debit)
    df["source_ifsc"] = df["customer_ifsc"].where(is_debit)
    df["source_bank_account"] = df["customer_bank_account"].where(is_debit)
    df["source_address"] = df["customer_address"].where(is_debit)
    df["source_city"] = df["customer_city"].where(is_debit)
    df["source_pincode"] = df["customer_pincode"].where(is_debit)

    # Target

    df["target_client_id"] = df["customer_client_id"].where(~is_debit)
    df["target_name"] = df["customer_name"].where(~is_debit)
    df["target_pan"] = df["customer_pan"].where(~is_debit)
    df["target_bank_name"] = df["customer_bank_name"].where(~is_debit)
    df["target_ifsc"] = df["customer_ifsc"].where(~is_debit)
    df["target_bank_account"] = df["customer_bank_account"].where(~is_debit)
    df["target_address"] = df["customer_address"].where(~is_debit)
    df["target_city"] = df["customer_city"].where(~is_debit)
    df["target_pincode"] = df["customer_pincode"].where(~is_debit)

    


    # SETTING ALERT FIELD

    df["alert_side"] = is_debit.map({
    True: SOURCE,
    False: TARGET
    })

    df["alert_client_id"] = df["customer_client_id"]
    df["alert_name"] = df["customer_name"]
    df["alert_pan"] = df["customer_pan"]



    # HANDLE MISSING COLUMN

    for column in FIU_ALERT_COLUMNS:
        if column not in df.columns:
            df[column] = None

    df = df[FIU_ALERT_COLUMNS]

    return df


# ---------------------------------------------------------
# FIU-2
# ---------------------------------------------------------

def _parse_cdsl_fiu2(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    """
    Handles FIU-2.
    """

    df = df.copy()

    # Normalize columns
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )

    # Rename
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # FIU-2 specific logic

    # ---------------------------------------------------------
    # Cleaning
    # ---------------------------------------------------------

    # Customer
    df["customer_pan"] = df["customer_pan"].apply(clean_pan)
    df["customer_name"] = df["customer_name"].apply(clean_name)
    df["customer_bank_account"] = df["customer_bank_account"].apply(clean_account_number)
    df["customer_bank_name"] = df["customer_bank_name"].apply(clean_name)
    df["customer_ifsc"] = df["customer_ifsc"].apply(clean_ifsc)
    df["customer_address"] = df["customer_address"].apply(clean_address)
    df["customer_city"] = df["customer_city"].apply(clean_city)
    df["customer_pincode"] = df["customer_pincode"].apply(clean_pincode)

    # Security
    df["isin_code"] = df["isin_code"].apply(clean_isin)
    df["isin_name"] = df["isin_name"].apply(clean_security_name)

    numeric_cols = [
    "quantity",
    "isin_price",
    "valuation"
]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)

    df["source_client_id"] = df["customer_client_id"]
    df["source_name"] = df["customer_name"]
    df["source_pan"] = df["customer_pan"]

    df["source_bank_name"] = df["customer_bank_name"]
    df["source_ifsc"] = df["customer_ifsc"]
    df["source_bank_account"] = df["customer_bank_account"]

    df["source_address"] = df["customer_address"]
    df["source_city"] = df["customer_city"]
    df["source_pincode"] = df["customer_pincode"]


    df["alert_client_id"] = df["customer_client_id"]
    df["alert_name"] = df["customer_name"]
    df["alert_pan"] = df["customer_pan"]

    df["alert_side"] = UNKNOWN

    for column in FIU_ALERT_COLUMNS:
        if column not in df.columns:
            df[column] = None

    df = df[FIU_ALERT_COLUMNS]

    return df