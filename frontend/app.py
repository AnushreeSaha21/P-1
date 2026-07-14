import sys
import streamlit as st

from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))



from pages.upload import show_upload
from pages.city import show_city


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
        "City",
        
    ]
)


# ---------------------------------------------------------
# Route Pages
# ---------------------------------------------------------

if page == "Upload":
    show_upload()


elif page == "City":
    show_city()



