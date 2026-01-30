import streamlit as st
from fpdf import FPDF
import re
import os
import io

# --- 1. SMART TEXT PARSER ---
@st.cache_data
def load_custom_data():
    data_map = {
        "USERS": {}, "DESIG": [], "TRADE": [], 
        "G_TYPE": [], "AUTH_Y": [], "AUTH_Z": []
    }
    if not os.path.exists("data.txt"):
        return data_map

    current_section = None
    try:
        with open("data.txt", "r", encoding="utf-8-sig") as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line: continue
                if clean_line == "USER_LIST": current_section = "USERS"
                elif clean_line == "DESIGNATIONS": current_section = "DESIG"
                elif clean_line == "TRADES": current_section = "TRADE"
                elif clean_line == "GRIEVANCE_TYPES": current_section = "G_TYPE"
                elif clean_line == "AUTHORITIES_Y": current_section = "AUTH_Y"
                elif clean_line == "AUTHORITIES_Z": current_section = "AUTH_Z"
                elif current_section == "USERS" and "," in clean_line:
                    uid, uname = clean_line.split(",", 1)
                    data_map["USERS"][uid.strip().upper()] = uname.strip()
                elif current_section:
                    data_map[current_section].append(clean_line)
    except Exception: pass
    return data_map

data = load_custom_data()

# --- 2. VIBRANT RAILWAY THEME & HORIZONTAL LAYOUT ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    /* Gradient Background */
    .stApp { background: linear-gradient(135deg, #003366 0%, #0066cc 100%); }
    
    /* Global White Box Sections */
    .white-section {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }

    /* Horizontal Label Styling */
    .row-container {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    label {
        color: #003366 !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        min-width: 200px; /* Forces labels to take equal space */
        margin-bottom: 0px !important;
    }

    /* Force Pure White Text Boxes & Dropdowns */
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #003366 !important;
        border-radius: 5px !important;
    }

    /* Make Dropdown Arrow Visible */
    svg[title="open"] { fill: #003366 !important; scale: 1.5; }

    /* Header Styling */
    .header-box {
        text-align: center;
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 30px;
        border-bottom: 5px solid #ffcc00; /* Railway Yellow */
    }
    .section-title {
        background-color: #ffcc00;
        color: #003366;
        padding: 5px 15px;
        font-weight: 900;
        border-radius: 5px;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN INTERFACE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
