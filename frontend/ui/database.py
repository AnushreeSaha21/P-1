import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from backend.services.database_service import (
    browse_database
)



def show_grid(df):

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True
    )

    # Wrap only the FIU Alerts column if it exists
    if "FIU Alerts" in df.columns:
        gb.configure_column(
            "FIU Alerts",
            wrapText=True,
            autoHeight=True,
            flex=1,
            minWidth=600,
            cellStyle={
                "white-space": "normal",
                "line-height": "20px"
            }
        )

    grid_options = gb.build()

    AgGrid(
        df,
        gridOptions=grid_options,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        height=500
    )

def show_database():

    st.title("🗄 FIU Database")

    st.write(
        "Browse all uploaded FIU transactions."
    )

    st.divider()

    if "page" not in st.session_state:
        st.session_state.page = 1

    if "search_clicked" not in st.session_state:
        st.session_state.search_clicked = False

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        report_year = st.text_input("Year",
    key="report_year")

    MONTHS = {
        "": None,
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    with col2:
        selected_month = st.selectbox(
            "Month",
            list(MONTHS.keys()),
            key="report_month"
        )

    report_month = MONTHS[selected_month]

    with col3:
        report_fortnight = st.selectbox(
        "Fortnight",
        ["", 1, 2],
    key="report_fortnight"
    )

    with col4:
        fiu_alert_type = st.selectbox(
        "Alert Type",
        ["", 1, 2, 3, 4, 5],
    key="fiu_alert_type"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        source_system = st.selectbox(
            "Depository",
            ["", "NSDL", "CDSL"],
    key="source_system"
        )

    with col2:
        transaction_indicator = st.selectbox(
            "Txn",
            ["", "Debit", "Credit"],
    key="transaction_indicator"
        )

    with col3:
        source_pan = st.text_input("Source PAN",
    key="source_pan")

    with col4:
        target_pan = st.text_input("Target PAN",
    key="target_pan")

    col1, col2 = st.columns(2)

    with col1:
        source_name = st.text_input("Source Name",
    key="source_name")

    with col2:
        target_name = st.text_input("Target Name",
        key="target_name")

    col1, col2 = st.columns(2)

    with col1:
        source_dp_id = st.text_input("Source DP ID",
    key="source_dp_id")

    with col2:
        target_dp_id = st.text_input("Target DP ID",
    key="target_dp_id")

    col1, col2 = st.columns(2)

    with col1:
        source_client_id = st.text_input(
            "Source BO ID",
    key="source_client_id"
        )

    with col2:
        target_client_id = st.text_input(
            "Target BO ID",
    key="target_client_id"
        )

    col1, col2 = st.columns(2)

    with col1:
        isin_code = st.text_input("ISIN Code",
    key="isin_code")

    with col2:
        isin_name = st.text_input("Security",
    key="isin_name")

    col1, col2 = st.columns([1, 1])

    with col1:
        search = st.button(
            "🔍 Search",
            use_container_width=True,
            type="primary"
        )

    with col2:
        clear = st.button(
            "🗑️ Clear",
            use_container_width=True
        )

    if clear:
        keys = [
            "report_year",
            "report_month",
            "report_fortnight",
            "fiu_alert_type",
            "source_system",
            "transaction_indicator",
            "source_pan",
            "target_pan",
            "source_name",
            "target_name",
            "source_dp_id",
            "target_dp_id",
            "source_client_id",
            "target_client_id",
            "isin_code",
            "isin_name",
        ]

        
        
        for key in keys:
            st.session_state.pop(key, None)

        st.session_state.search_clicked = False
        st.session_state.page = 1

        st.rerun()
    
    

    if search:
        st.session_state.search_clicked = True
        st.session_state.page = 1

    if st.session_state.search_clicked:


        result = browse_database(

            page=st.session_state.page,

            report_year=report_year or None,
            report_month=report_month or None,
            report_fortnight=report_fortnight or None,

            fiu_alert_type=fiu_alert_type or None,
            source_system=source_system or None,

            source_dp_id=source_dp_id or None,
            source_client_id=source_client_id or None,
            source_pan=source_pan or None,
            source_name=source_name or None,

            target_dp_id=target_dp_id or None,
            target_client_id=target_client_id or None,
            target_pan=target_pan or None,
            target_name=target_name or None,

            transaction_indicator=transaction_indicator or None,

            isin_code=isin_code or None,
            isin_name=isin_name or None
        )


        columns = [

                "Report Year",
                "Report Month",
                "Fortnight",

                "Depository",
                "Alert Type",

                "Source DP ID",
                "Source BO ID",
                "Source PAN",
                "Source Name",

                "Target DP ID",
                "Target BO ID",
                "Target PAN",
                "Target Name",

                "Txn",
                "Transaction Type",

                "ISIN Code",
                "Security",

                "Quantity",
                "Valuation"
            ]

        df = pd.DataFrame(
                result["records"],
                columns=columns
            )
        
        pan_df = result["pan_report"]

        isin_df = result["isin_report"]

        tab1, tab2, tab3 = st.tabs(
            [
                "📋 Transactions",
                "👤 PAN History",
                "📄 ISIN History"
            ]
        )

        # st.divider()

        with tab1:
            st.subheader("📋 Transactions")
            st.metric(
                    "Total Records",
                    result["total_records"]
                )
            
            start = (st.session_state.page - 1) * result["page_size"] + 1
            end = min(
            st.session_state.page * result["page_size"],
            result["total_records"]
            )

            st.caption(
                f"Showing records {start:,}–{end:,} of {result['total_records']:,}"
            )

            st.dataframe(
                    df,
                    use_container_width=True
                )

            col1, col2, col3 = st.columns([1, 2, 1])

            total_pages = max(
                1,
                (result["total_records"] + result["page_size"] - 1)
                // result["page_size"]
            )

            with col1:
                if st.button(
                    "⬅ Previous",
                    disabled=st.session_state.page == 1
                ):
                    st.session_state.page -= 1
                    st.rerun()

            with col2:
                st.markdown(
                    f"<div style='text-align:center;'>Page {st.session_state.page} of {total_pages}</div>",
                    unsafe_allow_html=True,
                )

            with col3:
                if st.button(
                    "Next ➡",
                    disabled=st.session_state.page >= total_pages
                ):
                    st.session_state.page += 1
                    st.rerun()

        # st.divider()



        
        with tab2:
            st.subheader("👤 PAN History")
            show_grid(pan_df)
        # st.divider()

        

        with tab3:
            st.subheader("📄 ISIN History")
            show_grid(isin_df)