import streamlit as st
import plotly.express as px

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