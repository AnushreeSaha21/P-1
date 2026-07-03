
import re


def is_valid_pan(pan):
    if pan is None:
        return False

    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan))


def is_valid_ifsc(ifsc):
    if ifsc is None:
        return False

    return bool(re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", ifsc))


def is_valid_isin(isin):
    if isin is None:
        return False

    return bool(re.fullmatch(r"[A-Z]{2}[A-Z0-9]{10}", isin))


def is_valid_pincode(pin):
    if pin is None:
        return False

    return bool(re.fullmatch(r"\d{6}", str(pin)))


def is_positive_number(value):
    try:
        return float(value) >= 0
    except Exception:
        return False

