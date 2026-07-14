
"""
nsdl_parser.py

Transforms raw NSDL FIU Excel data into the
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
    clean_isin,
    clean_numeric,
    clean_security_name
)

from backend.cleaning.standardizer import (
    standardize_transaction_indicator,
    standardize_transaction_type,
    standardize_market_type
    
)

from backend.utils.constants import (
    DEBIT,
    FIU_ALERT_COLUMNS,
    SOURCE,
    TARGET
)

# ---------------------------------------------------------
# NSDL COLUMN MAPPING
# ---------------------------------------------------------

COLUMN_MAPPING = {

    # Source

    "SOURCE DP ID": "source_dp_id",
    "SOURCE BNFC AC NO.": "source_client_id",
    "SOURCE FIRST HOLDER NAME": "source_name",
    "SOURCE I ST PAN": "source_pan",
    "NAME OF BANK OF SELLER": "source_bank_name",
    "NAME OF BRANCH OF SELLER": "source_branch_name",
    "ACCOUNT NO OF SELLER": "source_bank_account",
    "SOURCE CLIENT ADDRESS": "source_address",
    "SOURCE CITY": "source_city",
    "SOURCE PINCODE": "source_pincode",

    # Target

    "TARGET DP ID": "target_dp_id",
    "TARGET BNFC AC NO": "target_client_id",
    "TARGET FIRST HOLDER NAME": "target_name",
    "TARGET I ST PAN": "target_pan",
    "NAME OF BANK OF PURCHASER": "target_bank_name",
    "NAME OF BRANCH OF PURCHASER": "target_branch_name",
    "ACCOUNT NO FOR PURCHASER": "target_bank_account",
    "TARGET CLIENT ADDRESS": "target_address",
    "TARGET CITY": "target_city",
    "TARGET PINCODE": "target_pincode",

    # Transaction

    "TRAN TYPE": "transaction_type",
    "CR DB IND": "transaction_indicator",
    "MARKET TYPE": "market_type",

    # Security

    "ISIN": "isin_code",
    "SCRIP NAME": "isin_name",
    "QTY": "quantity",
    "ISIN PRICE": "isin_price",
    "VALUATION": "valuation",

    # Totals

    "MARKET TOTAL": "market_total",
    "REMAT TOTAL": "remat_total",
    "DEMAT TOTAL": "demat_total",
    "CA TOTAL": "ca_total",
    "IPO TOTAL": "ipo_total",
    "CONFIS TOTAL": "confis_total"

}


# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------

def parse_nsdl(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    """
    Converts raw NSDL DataFrame into
    canonical FIU DataFrame.
    """

    # Work on a copy
    df = df.copy()

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )

    # Rename to canonical names
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    # print(df.columns.tolist())
    # print(df[["isin_code"]].head())

    # ---------------------------------------------------------
    # Add Missing Database Columns
    # ---------------------------------------------------------


    for column in FIU_ALERT_COLUMNS:
        if column not in df.columns:
            df[column] = None

    #---------------------------------------------------------------------------------------------------------
    # CLEANING THE DATAFRAMES
    #---------------------------------------------------------------------------------------------------------

    cleaning_map = {
    # Source
    "source_pan": clean_pan,
    "source_name": clean_name,
    "source_bank_account": clean_account_number,
    "source_address": clean_address,
    "source_city": clean_city,
    "source_pincode": clean_pincode,
    "source_bank_name": clean_name,
    "source_branch_name": clean_name,

    # Target
    "target_pan": clean_pan,
    "target_name": clean_name,
    "target_bank_account": clean_account_number,
    "target_address": clean_address,
    "target_city": clean_city,
    "target_pincode": clean_pincode,
    "target_bank_name": clean_name,
    "target_branch_name": clean_name,

    # Security
    "isin_code": clean_isin,
    "isin_name": clean_security_name,
}

    for col, cleaner in cleaning_map.items():
        if col in df.columns:
            df[col] = df[col].apply(cleaner)


    if "market_type" in df.columns:
        df["market_type"] = df["market_type"].apply(
        standardize_market_type
        )

    # Numeric
    numeric_cols = [
        "quantity",
        "isin_price",
        "valuation",
        "market_total",
        "remat_total",
        "demat_total",
        "ca_total",
        "ipo_total",
        "confis_total"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)

    # Standardize
    if "transaction_indicator" in df.columns:
        df["transaction_indicator"] = df["transaction_indicator"].apply(
        standardize_transaction_indicator
        )

    if "transaction_type" in df.columns:
        df["transaction_type"] = df["transaction_type"].apply(
        standardize_transaction_type
        )



    # ---------------------------------------------------------
    # Derive Alert Account
    # ---------------------------------------------------------

#     is_debit = df["transaction_indicator"] == DEBIT

#     # Which side generated the alert
#     df["alert_side"] = is_debit.map({
#         True: SOURCE,
#         False: TARGET
#     })

#     # Alert PAN
#     # df["alert_pan"] = df["source_pan"].where(
#     #     is_debit,
#     #     df["target_pan"]
#     # )

#     df["alert_pan"] = None

#     # Debit -> source
#     df.loc[is_debit, "alert_pan"] = df.loc[
#         is_debit,
#         "source_pan"
#     ]

#     # Credit -> target
#     df.loc[~is_debit, "alert_pan"] = df.loc[
#         ~is_debit,
#         "target_pan"
#     ]

#     # Fallback: if target missing, use source
#     df["alert_pan"] = (
#         df["alert_pan"]
#         .fillna(df["source_pan"])
#         .fillna(df["target_pan"])
#     )

#     # Alert Name
#     df["alert_name"] = df["source_name"].where(
#         is_debit,
#         df["target_name"]
#     )

#     df["alert_name"] = (
#     df["alert_name"]
#     .fillna(df["source_name"])
#     .fillna(df["target_name"])
# )

    is_debit = df["transaction_indicator"] == DEBIT

    df["alert_pan"] = None
    df["alert_side"] = None

    # Debit -> source
    df.loc[is_debit, "alert_pan"] = df.loc[
        is_debit,
        "source_pan"
    ]

    df.loc[is_debit, "alert_side"] = SOURCE


    # Non-debit -> target
    df.loc[~is_debit, "alert_pan"] = df.loc[
        ~is_debit,
        "target_pan"
    ]

    df.loc[~is_debit, "alert_side"] = TARGET


    # Fallback source
    source_fallback = (
        df["alert_pan"].isna()
        & df["source_pan"].notna()
    )

    df.loc[source_fallback, "alert_pan"] = df.loc[
        source_fallback,
        "source_pan"
    ]

    df.loc[source_fallback, "alert_side"] = SOURCE


    # Fallback target
    target_fallback = (
        df["alert_pan"].isna()
        & df["target_pan"].notna()
    )

    df.loc[target_fallback, "alert_pan"] = df.loc[
        target_fallback,
        "target_pan"
    ]

    df.loc[target_fallback, "alert_side"] = TARGET

    # Alert Client ID
    df["alert_client_id"] = df["source_client_id"].where(
            is_debit,
            df["target_client_id"]
        )
    
    df["alert_name"] = df["source_name"].where(
    is_debit,
    df["target_name"]
)

    df["alert_name"] = (
        df["alert_name"]
        .fillna(df["source_name"])
        .fillna(df["target_name"])
    )

    # ---------------------------------------------------------
    # Reorder Columns
    # ---------------------------------------------------------

    df = df[FIU_ALERT_COLUMNS]

    print("NSDL alert PAN null count:")
    print(df["alert_pan"].isna().sum())

    print("Total rows:")
    print(len(df))

    print("Transaction indicators:")
    print(df["transaction_indicator"].value_counts(dropna=False))

    print(df[[
        "source_pan",
        "target_pan",
        "transaction_indicator",
        "alert_pan"
    ]].head(10))

    return df