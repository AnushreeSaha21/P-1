import streamlit as st
import pandas as pd

def show_user_guide():

    st.title("📖 FIU Analytics User Guide")

    st.success(
        """
        Welcome to **FIU Depository Analytics**.

        This application is designed to upload, process, store, search and analyze
        Financial Intelligence Unit (FIU) alert reports received from
        NSDL and CDSL.

        Use the navigation menu on the left to access the different modules.
        """
    )

    st.divider()

    st.header("📌 Application Overview")

    st.markdown(
    """
    FIU Depository Analytics is an internal web application developed to:

    - Upload FIU alert reports received from NSDL and CDSL.
    - Automatically validate and standardize uploaded data.
    - Store historical FIU alerts in a centralized PostgreSQL database.
    - Search alerts using multiple filters.
    - Analyze historical trends through interactive dashboards.
    """
    )

    st.header("📤 Upload Module")

    with st.expander("Features", expanded=True):

        st.markdown(
        """
    - Upload NSDL and CDSL FIU reports.

    - Automatic file validation.

    - Automatic data cleaning and standardization.

    - Duplicate upload detection.

    - Bulk storage into PostgreSQL.

    - Upload Intelligence Report generation.

    - PAN-wise historical analysis.

    - ISIN-wise historical analysis.
    """
        )

    st.header("🗄 Database Module")

    with st.expander("Features", expanded=True):

        st.markdown(
        """
    - Search alerts using multiple filters.

    - Search by PAN, Name, DP ID, BO ID, ISIN and Security Name.

    - View complete transaction details.

    - PAN-wise historical summary.

    - ISIN-wise historical summary.

    - Pagination for large datasets.
    """
        )

    st.header("📊 Analytics Module")

    with st.expander("Available Visualizations", expanded=True):

        st.markdown(
    """
    ### 📄 KPI Cards

    Provides a quick overview of

    - Total Alerts
    - Unique PANs
    - Unique ISINs
    - Unique Cities

    ---

    ### 🏙 Top Cities

    Displays cities having the highest number of reported FIU alerts.

    ---

    ### 📈 Monthly Trend

    Displays month-wise trend of reported alerts.

    ---

    ### 👤 Top PANs

    Displays PANs with the highest alert frequency.

    ---

    ### 📄 Top ISINs

    Displays securities having the highest alert frequency.

    ---

    ### 🌍 City Heatmap

    Displays month-wise distribution of alerts across cities.
    """
    )

    st.header("🚨 FIU Alert Types")

    st.markdown("###  Alert type-1")

    st.info(
        "Details of debit and credit transactions due to off-market or inter- depository transfer transactions, having value of Rs. 10 Lakh and above in an amount in an ISIN, in a single transaction or series of transactions executed during the fortnight."
    )

    st.markdown("###  Alert type-2")

    st.info(
        "Details of debit and credit transactions due to demat,remat and pledge involving 50000 or more shares, in an account in an ISIN, in a single transaction or series of transactions executed during the fortnight."
    )

    st.markdown("###  Alert type-3")
    
    st.info(
            "Details of debit and credit transactions involving 100000 shares or more or having value of Rs. 10 lakhs and above whichever is smaller in an account, in an ISIN, which exceed 10 times the avg size of the transaction calculated for the previous months transactions."
        )

    st.markdown("###  Alert type-4")
    
    st.info(
            "Details of off market transactions (within CDSL and inter-depository) where there are more than 20 transactions in an account for the past fortnight."
        )

    st.markdown("###  Alert type-5")
    
    st.info(
            "Any debit transaction in dormant account for more than 50000 shares or rs. 5 lakhs whichever is smaller will be reported as an alert. An account having no 'debit transaction' in the last 12 months will be considered as ' dormant' account for this purpose."
        )


    st.header("🔍 Search Tips")

    st.info(
    """
    • Leave filters blank to search the complete database.

    • Partial PAN and Name searches are supported.

    • Combine multiple filters to narrow search results.

    • Analytics are generated from all uploaded FIU records.
    """
    )

    st.header("⚠ Notes")

    st.warning(
    """
    • Duplicate files cannot be uploaded.

    • Uploaded data is standardized before storage.

    • Only validated records are stored in the database.

    • Analytics are automatically updated after new uploads.
    """
    )

    st.divider()

    st.markdown("""
    **Version 1.0**

    Developed by  
    **Anushree Saha**

    Data Science Intern

    Project completed under the guidance of  
    **Bedobani Chaudhari**  
    *Additional Director*
    """)