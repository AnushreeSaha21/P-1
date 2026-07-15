# Source Systems
CDSL = "CDSL"
NSDL = "NSDL"

# Transaction Indicators
DEBIT = "DR"
CREDIT = "CR"

# FIU Alert Types
FIU_1 = 1
FIU_2 = 2
FIU_3 = 3
FIU_4 = 4
FIU_5 = 5

# Transaction Types
DRCR_SUM = "DRCR_SUM"
DRCR_AVG_SUM = "DRCR_AVG_SUM"
PLEDGE = "PLEDGE"
OFF_MARKET = "OFF_MARKET"

# Fortnight
FIRST_FORTNIGHT = 1
SECOND_FORTNIGHT = 2

FIU_ALERT_COLUMNS = [
    "source_dp_id",
    "source_client_id",
    "source_name",
    "source_pan",
    "source_bank_name",
    "source_branch_name",
    "source_ifsc",
    "source_bank_account",
    "source_address",
    "source_city",
    "source_pincode",

    "target_dp_id",
    "target_client_id",
    "target_name",
    "target_pan",
    "target_bank_name",
    "target_branch_name",
    "target_ifsc",
    "target_bank_account",
    "target_address",
    "target_city",
    "target_pincode",

    "alert_side",
    "alert_client_id",
    "alert_name",
    "alert_pan",

    "transaction_indicator",
    "transaction_type",
    "market_type",

    "isin_code",
    "isin_name",
    "quantity",
    "isin_price",
    "valuation",

    "market_total",
    "remat_total",
    "demat_total",
    "ca_total",
    "ipo_total",
    "confis_total",
    "grand_total"
]

SOURCE = "SOURCE"
TARGET = "TARGET"
UNKNOWN = "UNKNOWN"