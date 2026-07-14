import tempfile
import streamlit as st
import sys
from pathlib import Path

import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.upload_service import upload_file



def show_upload():

    st.title("📤 Upload FIU File")

    st.write(
        "Upload NSDL or CDSL FIU Excel files into the FIU Depository database."
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Select FIU Excel File",
        type=["xls", "xlsx","csv"]
    )

    password = st.text_input(
        "Password (Leave blank if not required)",
        type="password"
    )

    upload_button = st.button(
        "Upload",
        use_container_width=True
    )


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

            # st.write(temp_path)

            result = upload_file(
                temp_path,
                password if password else None
            )

            st.success("File uploaded successfully!")
            st.write(f"**File ID:** {result['file_id']}")
            st.write(f"**Rows Inserted:** {result['rows_inserted']}")

            st.subheader("Upload Summary")
            summary = result["summary"]
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Rows Uploaded",
                    summary["Rows Uploaded"]
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

            st.subheader("Upload Intelligence Report")

            st.dataframe(
                result["report"],
                use_container_width=True
            )

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
                width="stretch"
            )

        except Exception as e:

            st.error(str(e))

        finally:

            if os.path.exists(temp_path):
                os.remove(temp_path)