import pandas as pd
import calendar

from backend.database.db_connection import get_connection

from backend.repositories.analytics_repository import (
    get_top_cities,
    get_monthly_trend,
    get_top_pans,
    get_top_isins,
    get_city_heatmap,
    get_kpi_cards
)


def load_analytics():

    connection = None

    try:

        connection = get_connection()
        month_map = dict(enumerate(calendar.month_abbr))

        city_rows = get_top_cities(connection)

        city_df = pd.DataFrame(
            city_rows,
            columns=[
                "City",
                "Alerts"
            ]
        )

        trend_rows = get_monthly_trend(connection)

        trend_df = pd.DataFrame(

            trend_rows,

            columns=[
                "Year",
                "Month",
                "Alerts"
            ]
        )

        trend_df["Period"] = (
            trend_df["Month"].map(month_map)
            + " "
            + trend_df["Year"].astype(str)
        )

        pan_rows = get_top_pans(connection)

        pan_df = pd.DataFrame(

            pan_rows,

            columns=[
                "PAN",
                "Alerts"
            ]
        )

        isin_rows = get_top_isins(connection)

        isin_df = pd.DataFrame(
            isin_rows,
            columns=[
                "ISIN",
                "Alerts"
            ]
        )

        heatmap_rows = get_city_heatmap(connection)

        heatmap_df = pd.DataFrame(

            heatmap_rows,

            columns=[
                "City",
                "Year",
                "Month",
                "Alerts"
            ]
        )

        heatmap_df["Period"] = (
            heatmap_df["Month"].map(month_map)
            + " "
            + heatmap_df["Year"].astype(str)
        )

        heatmap = heatmap_df.pivot(
            index="City",
            columns=["Year", "Month"],
            values="Alerts"
        ).fillna(0)

        heatmap = heatmap.sort_index(axis=1)

        heatmap.columns = [
            f"{month_map[m]} {y}"
            for y, m in heatmap.columns
        ]

        kpis = get_kpi_cards(connection)

        return {

            "cities": city_df,

            "monthly_trend": trend_df,

            "pans": pan_df,

            "isins": isin_df,

            "heatmap": heatmap,

            "kpis": kpis

        }

    finally:

        if connection:
            connection.close()