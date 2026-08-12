import tempfile
import streamlit as st
import sys
from pathlib import Path
import time
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.upload_service import upload_file


def show_upload():

    # =========================================================
    # SESSION STATE
    # =========================================================

    RESULT_TTL = 30 * 60   # 30 minutes

    if "upload_result" not in st.session_state:
        st.session_state.upload_result = None

    if "upload_result_time" not in st.session_state:
        st.session_state.upload_result_time = None

    # ---------------------------------------------------------
    # Check whether saved result has expired
    # ---------------------------------------------------------

    if (
        st.session_state.upload_result is not None
        and st.session_state.upload_result_time is not None
        and time.time() - st.session_state.upload_result_time > RESULT_TTL
    ):
        st.session_state.upload_result = None
        st.session_state.upload_result_time = None


    # =========================================================
    # PAGE
    # =========================================================

    st.title("📤 Upload FIU File")

    st.write(
        "Upload NSDL or CDSL FIU Excel files into the FIU Depository database."
    )

    st.divider()


    uploaded_file = st.file_uploader(
        "Select FIU Excel File",
        type=["xls", "xlsx", "csv"]
    )

    password = st.text_input(
        "Password (Leave blank if not required)",
        type="password"
    )

    upload_button = st.button(
        "Upload",
        use_container_width=True
    )


    # =========================================================
    # NEW UPLOAD
    # =========================================================

    if upload_button:

        if uploaded_file is None:

            st.warning("Please select an Excel file.")
            return

        temp_path = None

        try:

            temp_path = os.path.join(
                tempfile.gettempdir(),
                uploaded_file.name
            )

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())


            # ---------------------------------------------
            # Upload file
            # ---------------------------------------------

            result = upload_file(
                temp_path,
                password if password else None
            )


            # ---------------------------------------------
            # SAVE RESULT IN SESSION
            # ---------------------------------------------

            st.session_state.upload_result = result
            st.session_state.upload_result_time = time.time()


        except Exception as e:

            st.error(str(e))
            return

        finally:

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)


    # =========================================================
    # DISPLAY SAVED RESULT
    #
    # IMPORTANT:
    # This is OUTSIDE the upload_button block.
    # =========================================================

    result = st.session_state.upload_result

    if result is None:
        return


    # =========================================================
    # UPLOAD SUMMARY
    # =========================================================

    st.success("File uploaded successfully!")

    st.write(
        f"**File ID:** {result['file_id']}"
    )

    st.write(
        f"**Rows Inserted:** {result['rows_inserted']}"
    )


    # =========================================================
    # PAN HISTORY REPORT
    # =========================================================

    st.subheader("PAN History Report")

    summary = result["summary"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Transactions Uploaded",
            summary["Transactions Uploaded"]
        )

    with col2:
        st.metric(
            "Unique PANs",
            summary["Unique PANs"]
        )

    with col3:
        st.metric(
            "First-Time PANs",
            summary["First-Time PANs"]
        )


    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "Repeat PANs",
            summary["Repeat PANs"]
        )

    with col5:
        st.metric(
            "Historical Alerts",
            summary["Historical Alerts"]
        )

    with col6:
        st.metric(
            "New Alerts",
            summary["New Alerts"]
        )


    col7, _ = st.columns([1, 5])

    with col7:
        st.metric(
            "Total Alerts",
            summary["Total Alerts"]
        )


    st.divider()

    st.subheader("PAN History Details")

    st.dataframe(
        result["report"],
        use_container_width=True
    )


    # =========================================================
    # ISIN HISTORY REPORT
    # =========================================================

    st.divider()

    st.subheader("ISIN History Report")

    summary = result["isin_summary"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Transactions Uploaded",
            summary["Transactions Uploaded"]
        )

    with col2:
        st.metric(
            "Unique ISINs",
            summary["Unique ISINs"]
        )

    with col3:
        st.metric(
            "First-Time ISINs",
            summary["First-Time ISINs"]
        )

    with col4:
        st.metric(
            "Repeat ISINs",
            summary["Repeat ISINs"]
        )


    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric(
            "Historical Alerts",
            summary["Historical Alerts"]
        )

    with col6:
        st.metric(
            "New Alerts",
            summary["New Alerts"]
        )

    with col7:
        st.metric(
            "Total Alerts",
            summary["Total Alerts"]
        )


    st.dataframe(
        result["isin_report"],
        use_container_width=True
    )


    # =========================================================
    # CURRENT FILE TRANSACTIONS
    # =========================================================

    st.divider()

    st.subheader("Uploaded Transactions (Current File)")

    display_df = result["uploaded_data"].copy()

    display_columns = [

        "source_pan",
        "source_name",

        "target_pan",
        "target_name",

        "transaction_indicator",
        "transaction_type",

        "isin_code",
        "isin_name",

        "quantity",

        "valuation"

    ]

    display_df = display_df[display_columns]


    display_df = display_df.rename(columns={

        "source_pan": "Source PAN",
        "source_name": "Source Name",

        "target_pan": "Target PAN",
        "target_name": "Target Name",

        "transaction_indicator": "Txn",
        "transaction_type": "Transaction Type",

        "isin_code": "ISIN Code",
        "isin_name": "Security",

        "quantity": "Quantity",
        "valuation": "Valuation"

    })


    st.dataframe(
        display_df,
        use_container_width=True
    )


    # =========================================================
    # CLEAR RESULT
    # =========================================================

    st.divider()

    if st.button("🗑️ Clear Upload Result"):

        st.session_state.upload_result = None
        st.session_state.upload_result_time = None

        st.rerun()