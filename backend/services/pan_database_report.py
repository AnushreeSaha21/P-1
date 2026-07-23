"""
pan_database_report.py

Builds PAN-wise  report from uploaded FIU files.
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

def build_pan_database_report(
    rows
):
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

    # print(df.head())
    # print(df.dtypes)

    if df.empty:
        return pd.DataFrame()
    
    source_df = df[
        [
            "source_pan",
            "source_name",
            "fiu_alert_type",
            "report_year",
            "report_month",
            "report_fortnight"
        ]
    ].rename(
        columns={
            "source_pan": "pan",
            "source_name": "name"
        }
    )

    target_df = df[
        [
            "target_pan",
            "target_name",
            "fiu_alert_type",
            "report_year",
            "report_month",
            "report_fortnight"
        ]
    ].rename(
        columns={
            "target_pan": "pan",
            "target_name":"name"
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

   
    report = []

    for pan in pan_df["pan"].unique():
        group = pan_df[
            pan_df["pan"] == pan
        ]

        valid_names = group[
            group["name"].notna()
            & (group["name"].str.strip() != "")
        ]

        name = (
            valid_names.iloc[0]["name"]
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
            "PAN": pan,
            "Name": name,
            "Total Alerts": total_count,
            "FIU Alerts": "\n".join(alert_list)
        }
    )


    report_df = pd.DataFrame(report)
            
    report_df = report_df.sort_values(
        by="Total Alerts",
        ascending=False
    ).reset_index(drop=True)
    

    return  report_df

