"""
isin_database_report.py

Builds ISIN-wise report from FIU database.
"""

import calendar
import pandas as pd


def format_alert(row):

    month = calendar.month_abbr[row["report_month"]]

    fortnight = (
        "1st Fortnight"
        if row["report_fortnight"] == 1
        else "2nd Fortnight"
    )

    return (
        f"FIU-{row['fiu_alert_type']} "
        f"({fortnight}, {month} {row['report_year']})"
    )


def build_alert_list(df):

    formatted = df.apply(format_alert, axis=1)

    counts = formatted.value_counts()

    alerts = []

    for alert, count in counts.items():

        if count == 1:
            alerts.append(alert)

        else:
            alerts.append(
                f"{alert} [{count} Transactions]"
            )

    return alerts


def build_isin_database_report(rows):

    columns = [
        "report_year",
        "report_month",
        "report_fortnight",

        "source_system",
        "fiu_alert_type",

        "source_dp_id",
        "source_client_id",
        "source_pan",
        "source_name",

        "target_dp_id",
        "target_client_id",
        "target_pan",
        "target_name",

        "transaction_indicator",
        "transaction_type",

        "isin_code",
        "isin_name",

        "quantity",
        "valuation"
    ]

    df = pd.DataFrame(rows, columns=columns)

    if df.empty:
        return pd.DataFrame()

    isin_df = df[
        [
            "isin_code",
            "isin_name",
            "fiu_alert_type",
            "report_year",
            "report_month",
            "report_fortnight"
        ]
    ].copy()

    isin_df = isin_df.rename(
        columns={
            "isin_code": "isin",
            "isin_name": "security"
        }
    )

    isin_df = isin_df.dropna(
        subset=["isin"]
    )

    isin_df["isin"] = (
        isin_df["isin"]
        .astype(str)
        .str.strip()
    )

    isin_df = isin_df[
        ~isin_df["isin"].str.lower().isin(
            ["", "nan", "none"]
        )
    ]

    report = []

    for isin in isin_df["isin"].unique():

        group = isin_df[
            isin_df["isin"] == isin
        ]

        valid_names = group[
            group["security"].notna()
            & (group["security"].str.strip() != "")
        ]

        security = (
            valid_names.iloc[0]["security"]
            if not valid_names.empty
            else ""
        )

        group = group.sort_values(
            by=[
                "report_year",
                "report_month",
                "report_fortnight"
            ]
        )

        total_count = len(group)

        alert_list = build_alert_list(group)

        report.append(
            {
                "ISIN": isin,
                "Security": security,
                "Total Alerts": total_count,
                "FIU Alerts": "\n".join(alert_list)
            }
        )

    report_df = pd.DataFrame(report)

    report_df = report_df.sort_values(
        by="Total Alerts",
        ascending=False
    ).reset_index(drop=True)

    return report_df