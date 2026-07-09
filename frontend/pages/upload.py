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

            st.divider()

            st.subheader("Upload Intelligence Report")

            st.dataframe(
                result["report"],
                use_container_width=True
            )

            # st.markdown(
            #     result["report"].to_html(
            #     escape=False,
            #     index=False
            #     ),
            #     unsafe_allow_html=True
            # )

            st.write(f"**File ID:** {result['file_id']}")
            st.write(f"**Rows Inserted:** {result['rows_inserted']}")


        except Exception as e:

            st.error(str(e))

        finally:

            if os.path.exists(temp_path):
                os.remove(temp_path)