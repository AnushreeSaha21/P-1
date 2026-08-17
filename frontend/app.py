import sys
import streamlit as st

from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


from frontend.ui.upload import show_upload
from ui.analytics import show_analytics
from ui.database import show_database
from ui.user_guide import show_user_guide
from ui.network_analysis import show_network_analysis


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
    "Menu",
    [
        "Upload",
        "Analytics",
        "Database",
        "About",
        "NW"
        
    ]
)


# ---------------------------------------------------------
# Route Pages
# ---------------------------------------------------------

if page == "Upload":
    show_upload()


elif page == "Analytics":
    show_analytics()

elif page == "Database":
    show_database()

elif page == "About":
    show_user_guide()

elif page == "NW":
    show_network_analysis()




