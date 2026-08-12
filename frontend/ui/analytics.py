import streamlit as st
import plotly.express as px
import pandas as pd

from backend.services.analytics_service import (
    load_analytics
)


def show_analytics():

    st.title("📊 FIU Analytics")

    analytics = load_analytics()

    kpis = analytics["kpis"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📄 Total Alerts",
            f"{kpis[0]:,}"
        )

    with col2:
        st.metric(
            "👤 Unique PANs",
            f"{kpis[1]:,}"
        )

    with col3:
        st.metric(
            "📑 Unique ISINs",
            f"{kpis[2]:,}"
        )

    with col4:
        st.metric(
            "🏙️ Unique Cities",
            f"{kpis[3]:,}"
        )

    st.divider()

    city_df = analytics["cities"]

    trend_df = analytics["monthly_trend"]

    col1, col2 = st.columns(2)

    with col1:
        # Top Cities

        fig = px.bar(
                city_df,
                x="Alerts",
                y="City",
                orientation="h",
                text="Alerts",
                color="Alerts",
                color_continuous_scale="Sunset"
            )
        
        fig.update_layout(
                title="🏙️ Top 20 Cities by Alert Count",
                xaxis_title="Number of Alerts",
                yaxis_title="City",
                template="plotly_white",
                height=550,
                coloraxis_showscale=False,
                yaxis=dict(categoryorder="total ascending"),
                margin=dict(l=20, r=20, t=60, b=20)
            )
        
        fig.update_traces(
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Alerts: %{x:,}<extra></extra>"
            )
        
        st.plotly_chart(
                fig,
                use_container_width=True
            )

    with col2:
        # Monthly Trend

        fig2 = px.line(

            trend_df,

            x="Period",

            y="Alerts",

            markers=True,

            title="📈 Monthly Alert Trend"
        )

        

        fig2.update_traces(

            line=dict(
                # color="#E76F51",
                width=3
            ),

            marker=dict(
                size=8,
                # color="#F4A261"
            ),

            hovertemplate = "<b>%{x}</b><br>Alerts: %{y:,}<extra></extra>",

            text=trend_df["Alerts"],

            textposition = "top center"
        )

        fig2.update_layout(

            template="plotly_white",

            title="📈 Monthly Alert Trend",

            xaxis_title="Reporting Month",

            yaxis_title="Number of Alerts",

            height=550
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    pan_df = analytics["pans"]
    isin_df = analytics["isins"]
    col3, col4 = st.columns(2)

    with col3:

        fig3 = px.bar(

            pan_df,

            x="Alerts",

            y="PAN",

            orientation="h",

            text="Alerts",

            color="Alerts",

            color_continuous_scale="Sunset"
        )

        fig3.update_layout(

            title="👤 Top 10 PANs",

            xaxis_title="Number of Alerts",

            yaxis_title="PAN",

            template="plotly_white",

            height=550,

            coloraxis_showscale=False,

            yaxis=dict(categoryorder="total ascending"),

            margin=dict(l=20, r=20, t=60, b=20)
        )

        fig3.update_traces(

            textposition="outside",

            hovertemplate="<b>%{y}</b><br>Alerts: %{x:,}<extra></extra>"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    with col4:

        fig4 = px.bar(

            isin_df,

            x="Alerts",

            y="ISIN",

            orientation="h",

            text="Alerts",

            color="Alerts",

            color_continuous_scale="Sunset"
        )

        fig4.update_layout(

            title="📄 Top 10 ISINs",

            xaxis_title="Number of Alerts",

            yaxis_title="ISIN",

            template="plotly_white",

            height=550,

            coloraxis_showscale=False,

            yaxis=dict(categoryorder="total ascending"),

            margin=dict(l=20, r=20, t=60, b=20)
        )

        fig4.update_traces(

            textposition="outside",

            hovertemplate="<b>%{y}</b><br>Alerts: %{x:,}<extra></extra>"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    heatmap = analytics["heatmap"]

    fig5 = px.imshow(

        heatmap,

        text_auto=True,

        color_continuous_scale="Sunset",

        aspect="auto",

        title="🌍 City-wise Monthly Heatmap"
    )

    fig5.update_layout(

        template="plotly_white",

        height=650
    )

    st.plotly_chart(

        fig5,

        use_container_width=True
    )


    st.divider()

    st.subheader("🤖 AI Analytics Insights")

    st.write(
        "Generate an AI-assisted interpretation of the analytics shown above."
    )

    # ---------------------------------------------------------
    # Prepare exact month-to-month changes for AI
    # ---------------------------------------------------------

    trend_for_ai = trend_df.copy()

    trend_for_ai["Period"] = pd.to_datetime(
        trend_for_ai["Period"]
    )

    trend_for_ai = trend_for_ai.sort_values("Period")

    monthly_changes = []

    for i in range(1, len(trend_for_ai)):

        previous = trend_for_ai.iloc[i - 1]
        current = trend_for_ai.iloc[i]

        previous_period = previous["Period"]
        current_period = current["Period"]

        # Only compare consecutive calendar months
        month_difference = (
            (current_period.year - previous_period.year) * 12
            + (current_period.month - previous_period.month)
        )

        if month_difference == 1:

            previous_alerts = int(previous["Alerts"])
            current_alerts = int(current["Alerts"])

            change = current_alerts - previous_alerts

            monthly_changes.append({
                "from": previous_period.strftime("%b %Y"),
                "to": current_period.strftime("%b %Y"),
                "from_alerts": previous_alerts,
                "to_alerts": current_alerts,
                "change": change,
                "direction": (
                    "increase"
                    if change > 0
                    else "decrease"
                    if change < 0
                    else "no change"
                )
            })

    largest_increase = max(
        monthly_changes,
        key=lambda x: x["change"],
        default=None
    )

    largest_decrease = min(
        monthly_changes,
        key=lambda x: x["change"],
        default=None
    )

    if st.button("🔎 Analyze Analytics"):

        analytics_context = {

            "kpis": {
                "total_alerts": int(kpis[0]),
                "unique_pans": int(kpis[1]),
                "unique_isins": int(kpis[2]),
                "unique_cities": int(kpis[3])
            },

            # -----------------------------------------------------
            # Top cities
            # -----------------------------------------------------

            "top_cities": city_df.to_dict(
                orient="records"
            ),

            # -----------------------------------------------------
            # Monthly data
            # -----------------------------------------------------

            "monthly_trend": trend_for_ai.to_dict(
                orient="records"
            ),

            "monthly_changes": monthly_changes,

            # -----------------------------------------------------
            # Top PANs
            # -----------------------------------------------------

            "top_pans": pan_df.to_dict(
                orient="records"
            ),

            # -----------------------------------------------------
            # Top ISINs
            # -----------------------------------------------------

            "top_isins": isin_df.to_dict(
                orient="records"
            ),

            "largest_monthly_increase": largest_increase,
            "largest_monthly_decrease": largest_decrease,
               
        }

        with st.spinner("Analyzing analytics..."):

            from backend.ai.ollama_service import (
                analyze_analytics
            )

            ai_result = analyze_analytics(
                analytics_context
            )

        st.markdown(ai_result)