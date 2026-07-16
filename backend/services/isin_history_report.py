"""
isin_history_report.py

Builds ISIN-wise history report from uploaded FIU files.
"""

import pandas as pd
import calendar

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

def build_isin_history_report(
    rows,
    current_file_id
):
    columns = [

    "isin_code",
    "isin_name",

    "file_id",

    "fiu_alert_type",

    "report_year",
    "report_month",
    "report_fortnight"
]

    df = pd.DataFrame(rows, columns=columns)
    if df.empty:
        return {
            "Transactions Uploaded": 0,
            "Unique ISINs": 0,
            "First-Time ISINs": 0,
            "Repeat ISINs": 0,
            "Historical Alerts": 0,
            "New Alerts": 0,
            "Total Alerts": 0,
        }, pd.DataFrame()

    df = df.dropna(subset=["isin_code"])

    df["isin_code"] = (
        df["isin_code"]
        .astype(str)
        .str.strip()
    )

    df = df[
        ~df["isin_code"].str.lower().isin(
            ["", "nan", "none"]
        )
    ]

    new_df = (
        df[
            df["file_id"] == current_file_id
        ]
        .drop_duplicates(subset=["isin_code"])
    )

    rows_uploaded = len(
        df[df["file_id"] == current_file_id]
    )

    unique_isins = len(
        new_df["isin_code"].unique()
    )

    report = []

    historical_alerts = 0
    first_time_isins = 0
    repeat_isins = 0
    new_alerts_total = 0
    total_alerts = 0

    for isin in new_df["isin_code"]:
        group = df[
            df["isin_code"] == isin
        ]

        valid_names = group[
            group["isin_name"].notna()
            & (group["isin_name"].str.strip() != "")
        ]

        security = (
            valid_names.iloc[0]["isin_name"]
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

        historical = group[group["file_id"] < current_file_id]

        new = group[group["file_id"] == current_file_id]

        historical_count = len(historical)

        new_count = len(new)

        total_count = historical_count + new_count

        historical_alerts += historical_count
        new_alerts_total += new_count
        total_alerts += total_count

        if historical_count == 0:
            first_time_isins += 1
        else:
            repeat_isins += 1


        previous_list = build_alert_list(historical)

        new_list = build_alert_list(new)

        
        max_rows = max(
            len(previous_list),
            len(new_list),
            1
        )

        latest_alert = format_alert(group.iloc[-1])

            
            
        for i in range(max_rows):

            report.append({

                    "ISIN Code": isin if i == 0 else "",

                    "Security": security if i == 0 else "",

                    "Total Alerts": total_count if i == 0 else "",

                    "New Alerts": new_count if i == 0 else "",

                    "Previous Alert": (
                        previous_list[i]
                        if i < len(previous_list)
                        else ""
                    ),

                    "Newly Uploaded Alert": (
                        new_list[i]
                        if i < len(new_list)
                        else ""
                    ),

                    "Latest Alert": (
                        latest_alert
                        if i == 0
                        else ""
                    )

                })


    report_df = pd.DataFrame(report)
           
    summary = {

            "Transactions Uploaded": rows_uploaded,

            "Unique ISINs": unique_isins,

            "First-Time ISINs": first_time_isins,

            "Repeat ISINs": repeat_isins,

            "Historical Alerts": historical_alerts,

            "New Alerts": new_alerts_total,

            "Total Alerts": total_alerts

        }

    return summary, report_df

