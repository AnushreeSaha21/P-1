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
    - Analyze transaction relationships between PANs using network analysis.
    """
    )

    # =========================================================
    # UPLOAD MODULE
    # =========================================================

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

    # =========================================================
    # DATABASE MODULE
    # =========================================================

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

    # =========================================================
    # ANALYTICS MODULE
    # =========================================================

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
        

        ---

        ### 🤖 AI Analytics Insights

        Provides an AI-assisted summary of the analytics displayed on
        the Analytics page.

        The AI analysis can briefly interpret:

        - Important concentrations in the displayed data.
        - Changes and trends over time.
        - Potentially notable patterns.
        - PANs, ISINs, or geographic areas that may deserve further review.
        - An evidence-based overall assessment based only on the supplied
          analytics data.

        The AI analysis is generated from the statistics and trends
        calculated by the application. It does not independently
        investigate the underlying transactions.

        AI-generated observations are intended to assist analysts in
        interpreting the displayed analytics and should not be treated
        as a determination of suspicious, fraudulent, illegal, or
        high-risk activity.

        """
        )

    # =========================================================
    # NETWORK ANALYSIS MODULE
    # =========================================================

    st.header("🧠 Network Analysis Module")

    with st.expander(
        "PAN Transaction Network Analysis",
        expanded=True
    ):

        st.markdown(
        """
        The **Network Analysis** module analyzes transaction relationships
        between PANs and helps investigators explore the structure of the
        transaction network.

        The network is represented as a directed graph where:

        - **PANs** are represented as nodes.
        - **Transactions between PANs** are represented as directed edges.
        - Edge information includes transaction counts, alerts, ISINs and
          reporting periods.

        ---

        ### 🔄 Circular Transaction Patterns

        Identifies transaction cycles where a transaction path eventually
        returns to the originating PAN.

        For example:

        `PAN A → PAN B → PAN C → PAN A`

        The circular transaction analysis displays:

        - Transaction cycle
        - PANs involved
        - Number of transactions
        - Common ISINs
        - Chronological information

        A selected cycle can also be visualized as an interactive network graph.

        ---

        ### 🔁 Reciprocal Relationships

        Identifies PAN pairs where transactions occur in both directions.

        For example:

        `PAN A → PAN B`

        and

        `PAN B → PAN A`

        The analysis provides:

        - PAN pair
        - Forward transaction count
        - Reverse transaction count
        - Total transaction count
        - ISIN information for both directions

        ---

        ### 🔗 Source-to-Target PAN Path

        Allows investigators to search for a directed transaction path
        between two PANs.

        The investigator can enter:

        - Source PAN
        - Target PAN

        The application searches the transaction network for a path between
        the supplied PANs.

        The source and target PAN values can also be swapped using the
        **Swap Source ↔ Target** option.

        The path analysis displays:

        - Transaction path
        - Number of PANs involved
        - Number of hops
        - Relationships between PANs
        - Transaction counts
        - Alert counts
        - ISINs
        - Reporting periods

        The path search supports self-loop and same-PAN searches where
        applicable.

        ---

        ### 🔎 PAN Explorer

        PAN Explorer allows an investigator to search for a specific PAN
        and examine its immediate transaction relationships.

        The visualization displays:

        - The selected PAN
        - Incoming relationships
        - Outgoing relationships
        - Connected PANs
        - Transaction counts
        - Alert counts
        - ISINs
        - Alert reporting periods

        The selected PAN is highlighted separately in the network
        visualization to make it easier to identify within the graph.

        ---

        ### 🌐 Interactive Network Visualization

        Network patterns can be explored through an interactive graph.

        The visualization supports:

        - Zooming in and out.
        - Panning across the graph.
        - Navigation controls.
        - Node movement.
        - Interactive relationship inspection.
        - Hover-based transaction information.

        Hovering over a transaction relationship provides information
        such as:

        - Source PAN
        - Target PAN
        - Transaction count
        - ISINs
        - Alert reporting periods

        ---

        ### 🤖 AI Network Insights

        The Network Analysis module also provides AI-assisted analysis of
        selected network patterns and PAN relationships.

        The AI summarizes supplied network information such as:

        - Incoming relationships
        - Outgoing relationships
        - Direct connections
        - Circular transaction involvement
        - Reciprocal relationship involvement
        - Self-loop involvement
        - Transaction observations
        - ISIN information

        The AI analysis is intended to summarize the observed network
        structure and identify **potential areas for further review**.

        AI-generated observations should be considered analytical assistance
        and not as a determination of suspicious, fraudulent or illegal
        activity.

        ---

        ### 🗄 Neo4j Network Graph

        The transaction network is represented in **Neo4j** for graph-based
        analysis.

        PostgreSQL remains the primary source for the FIU alert data, while
        the PAN relationship network is synchronized into Neo4j for
        efficient graph operations such as:

        - Relationship traversal
        - Circular pattern detection
        - Reciprocal relationship detection
        - PAN exploration
        - Multi-hop path searches
        """
        )

    # =========================================================
    # FIU ALERT TYPES
    # =========================================================

    st.header("🚨 FIU Alert Types")

    st.markdown("### Alert type-1")

    st.info(
        "Details of debit and credit transactions due to off-market or inter- depository transfer transactions, having value of Rs. 10 Lakh and above in an amount in an ISIN, in a single transaction or series of transactions executed during the fortnight."
    )

    st.markdown("### Alert type-2")

    st.info(
        "Details of debit and credit transactions due to demat,remat and pledge involving 50000 or more shares, in an account in an ISIN, in a single transaction or series of transactions executed during the fortnight."
    )

    st.markdown("### Alert type-3")

    st.info(
        "Details of debit and credit transactions involving 100000 shares or more or having value of Rs. 10 lakhs and above whichever is smaller in an account, in an ISIN, which exceed 10 times the avg size of the transaction calculated for the previous months transactions."
    )

    st.markdown("### Alert type-4")

    st.info(
        "Details of off market transactions (within CDSL and inter-depository) where there are more than 20 transactions in an account for the past fortnight."
    )

    st.markdown("### Alert type-5")

    st.info(
        "Any debit transaction in dormant account for more than 50000 shares or rs. 5 lakhs whichever is smaller will be reported as an alert. An account having no 'debit transaction' in the last 12 months will be considered as ' dormant' account for this purpose."
    )

    # =========================================================
    # SEARCH TIPS
    # =========================================================

    st.header("🔍 Search Tips")

    st.info(
    """
    • Leave filters blank to search the complete database.

    • Partial PAN and Name searches are supported.

    • Combine multiple filters to narrow search results.

    • Analytics are generated from all uploaded FIU records.
    """
    )

    # =========================================================
    # NOTES
    # =========================================================

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
    *(Data Science Intern)*

    Project completed under the guidance of  
    **Bedobani Chaudhari Mam**  
    *(Additional Director)*
    """)