"""
report_builder.py

Builds analytics reports from uploaded FIU alerts.
"""

import pandas as pd
import calendar


def format_alert(row) -> str:
    """
    Converts one alert row into a readable string.
    """

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



def build_upload_report(
    rows: list,
    current_file_id: int
):
    """
    Builds the Upload Intelligence Report.
    """

    columns = [
    "alert_pan",
    "alert_name",
    "file_id",
    "fiu_alert_type",
    "report_year",
    "report_month",
    "report_fortnight"
    ]

    df = pd.DataFrame(rows, columns=columns)
    if df.empty:
        return {}, pd.DataFrame()
    
    report = []

    new_df = df[df["file_id"] == current_file_id]

    rows_uploaded = len(new_df)

    unique_pans = len(new_df["alert_pan"].unique())

    first_time_pans = 0
    repeat_pans = 0
    historical_alerts = 0
    new_alerts_total = 0
    total_alerts = 0

    for pan in new_df["alert_pan"].unique():

        group = df[df["alert_pan"] == pan]

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

        # previous_alerts = "<br>".join(historical.apply(format_alert,axis=1))

        # new_alerts = "<br>".join(new.apply(format_alert,axis=1))

        previous_list = [
            format_alert(row)
            for _, row in historical.iterrows()
        ]

        new_list = [
            format_alert(row)
            for _, row in new.iterrows()
        ]

        max_rows = max(
            len(previous_list),
            len(new_list),
            1
        )

        latest_alert = format_alert(group.iloc[-1])

        # report.append({

        #     "PAN": pan,

        #     "Name": group.iloc[0]["alert_name"],

        #     "Historical": historical_count,

        #     "New": new_count,

        #     "Total": total_count,

        #     "Previous Alerts": previous_alerts,

        #     "Newly Uploaded Alerts": new_alerts,

        #     "Latest Alert": latest_alert

        # })

        for i in range(max_rows):

            report.append({

                "PAN": pan if i == 0 else "",

                "Name": group.iloc[0]["alert_name"] if i == 0 else "",

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

        # summary = {}

        # summary["Rows Uploaded"] = len(
        #     df[df["file_id"] == current_file_id]
        # )

        # summary["Unique PANs"] = len(report_df)

        # summary["First-Time PANs"] = (
        #     report_df["Historical"] == 0
        # ).sum()

        # summary["Repeat PANs"] = (
        #     report_df["Historical"] > 0
        # ).sum()

        # summary["Historical Alerts"] = report_df[
        #     "Historical"
        # ].sum()

        # summary["New Alerts"] = report_df[
        #     "New"
        # ].sum()

        # summary["Total Alerts"] = report_df[
        #     "Total"
        # ].sum()

    summary = {

        "Rows Uploaded": rows_uploaded,

        "Unique PANs": unique_pans,

        "First-Time PANs": first_time_pans,

        "Repeat PANs": repeat_pans,

        "Historical Alerts": historical_alerts,

        "New Alerts": new_alerts_total,

        "Total Alerts": total_alerts

    }

    return summary, report_df
