import sys
import streamlit as st

from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))



from pages.upload import show_upload
from pages.upload_history import show_upload_history
from pages.search import show_search
from pages.analytics import show_analytics

from PIL import Image

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).parent

logo = Image.open(BASE_DIR / "assets" / "logo.png")

st.set_page_config(
    page_title="FIU INDIA  Depository Analytics",
    page_icon=logo,
    layout="wide"
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("FIU INDIA Depository Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "Upload",
        "Upload History",
        "Search",
        "Analytics"
    ]
)


# ---------------------------------------------------------
# Route Pages
# ---------------------------------------------------------

if page == "Upload":
    show_upload()

elif page == "Upload History":
    show_upload_history()

elif page == "Search":
    show_search()

elif page == "Analytics":
    show_analytics()



