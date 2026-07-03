
import re
import pandas as pd


def clean_string(value):
    """Remove leading/trailing spaces."""
    if pd.isna(value):
        return None
    return str(value).strip()


def clean_name(name):
    """Remove extra spaces from names."""
    if pd.isna(name):
        return None

    name = str(name).strip()
    name = re.sub(r"\s+", " ", name)

    return name


def clean_pan(pan):
    """Trim spaces and convert PAN to uppercase."""
    if pd.isna(pan):
        return None

    pan = str(pan).strip().upper()

    return pan


def clean_ifsc(ifsc):
    """Remove spaces and convert IFSC to uppercase."""
    if pd.isna(ifsc):
        return None

    return str(ifsc).replace(" ", "").upper()


def clean_account_number(account):
    """
    Remove spaces, hyphens and dots from account numbers.
    """

    if pd.isna(account):
        return None

    account = str(account)

    account = account.replace(" ", "")
    account = account.replace("-", "")
    account = account.replace(".", "")

    return account


def clean_isin(isin):
    """Clean ISIN code."""
    if pd.isna(isin):
        return None

    return str(isin).strip().upper()


def clean_address(address):
    """Collapse multiple spaces inside addresses."""
    if pd.isna(address):
        return None

    address = str(address).strip()

    address = re.sub(r"\s+", " ", address)

    return address


def clean_city(city):
    """Trim city names."""
    if pd.isna(city):
        return None

    return str(city).strip()


def clean_pincode(pin):
    """Keep only digits."""
    if pd.isna(pin):
        return None

    return re.sub(r"\D", "", str(pin))


def clean_numeric(value):
    """
    Converts
    10,000
    10000
    10000.00

    into float.
    """

    if pd.isna(value):
        return None

    value = str(value)

    value = value.replace(",", "")

    try:
        return float(value)
    except ValueError:
        return None


def clean_security_name(value):
    """
    Cleans ISIN / Scrip names.
    Removes extra spaces but preserves case.
    """

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    return " ".join(value.split())
