
def standardize_name(name):
    """
    Rahul kumar
    RAHUL KUMAR

    ->
    Rahul Kumar
    """

    if name is None:
        return None

    return name.title()


def standardize_city(city):
    """
    DELHI
    new delhi

    ->
    Delhi
    New Delhi
    """

    if city is None:
        return None

    return city.title()


def standardize_transaction_indicator(value):
    """
    DR
    Debit
    debit

    ->
    DR

    CR
    Credit

    ->
    CR
    """

    if value is None:
        return None

    value = str(value).strip().upper()

    mapping = {
    "DR": "DR",
    "DB": "DR",          # NSDL abbreviation
    "DEBIT": "DR",

    "CR": "CR",
    "CRD": "CR",         # Optional, if encountered
    "CREDIT": "CR"
}

    if value not in mapping:
        raise ValueError(f"Unknown transaction indicator: {value}")

    return mapping[value]


def standardize_transaction_type(value):
    """
    Different transaction descriptions into one format.
    """

    if value is None:
        return None

    value = str(value).strip().upper()

    mapping = {
        "OFF MARKET": "OFF_MARKET",
        "OFFMARKET": "OFF_MARKET",
        "PLEDGE": "PLEDGE",
        "DEMAT": "DEMAT",
        "REMAT": "REMAT",
        "IPO": "IPO",
        "CA": "CA"
    }

    return mapping.get(value, value)


def standardize_market_type(value):
    """
    Standardize Market Type values.

    Returns None for missing values.
    Converts text to uppercase and removes extra spaces.
    """

    if value is None:
        return None

    value = str(value).strip().upper()

    if value == "":
        return None

    return value


