"""
pan_history_report.py

Builds PAN-wise history report from uploaded FIU files.
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

def build_pan_history_report(
    rows,
    current_file_id
):
    columns = [

    "source_pan",
    "target_pan",

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
            "Unique PANs": 0,
            "First-Time PANs": 0,
            "Repeat PANs": 0,
            "Historical Alerts": 0,
            "New Alerts": 0,
            "Total Alerts": 0,
        }, pd.DataFrame()
    
    source_df = df[
        [
            "source_pan",
            "file_id",
            "fiu_alert_type",
            "report_year",
            "report_month",
            "report_fortnight"
        ]
    ].rename(
        columns={
            "source_pan": "pan"
        }
    )

    target_df = df[
        [
            "target_pan",
            "file_id",
            "fiu_alert_type",
            "report_year",
            "report_month",
            "report_fortnight"
        ]
    ].rename(
        columns={
            "target_pan": "pan"
        }
    )

    pan_df = pd.concat(
        [
            source_df,
            target_df
        ],
        ignore_index=True
    )
    

    pan_df = pan_df.dropna(
        subset=["pan"]
    )

    pan_df["pan"] = (
        pan_df["pan"]
        .astype(str)
        .str.strip()
    )

    pan_df = pan_df[
        ~pan_df["pan"].str.lower().isin(
            ["", "nan", "none"]
        )
    ]

    new_df = (
        pan_df[
            pan_df["file_id"] == current_file_id
        ]
        .drop_duplicates(subset=["pan"])
    )

    rows_uploaded = len(
        df[df["file_id"] == current_file_id]
    )

    unique_pans = len(
        new_df["pan"].unique()
    )

    report = []

    first_time_pans = 0
    repeat_pans = 0

    historical_alerts = 0
    new_alerts_total = 0
    total_alerts = 0

    for pan in new_df["pan"]:
        group = pan_df[
            pan_df["pan"] == pan
        ]

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
            first_time_pans += 1
        else:
            repeat_pans += 1


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

                    "PAN": pan if i == 0 else "",

                    

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
            # report_df = report_df.sort_values(
            #     by=["PAN"],
            #     na_position="last"
            # )

    summary = {

            "Transactions Uploaded": rows_uploaded,

            "Unique PANs": unique_pans,

            "First-Time PANs": first_time_pans,

            "Repeat PANs": repeat_pans,

            "Historical Alerts": historical_alerts,

            "New Alerts": new_alerts_total,

            "Total Alerts": total_alerts

        }

    return summary, report_df

