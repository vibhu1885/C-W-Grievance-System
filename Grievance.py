import streamlit as st
from fpdf import FPDF
import pandas as pd
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

# --- 2. PROFESSIONAL DARK THEME (HIGH VISIBILITY) ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    /* Dark Command Center Background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Login & Form Containers */
    .stForm {
        background-color: #161b22;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #30363d;
    }

    /* Input Field Labels - Railway Gold for Visibility */
    label {
        color: #ffcc00 !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        margin-bottom: 5px !important;
    }

    /* Force Pure White Text Boxes for Data Entry */
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #ffcc00 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* Section Headers */
    .section-header {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 900;
        border-bottom: 3px solid #ffcc00;
        margin-bottom: 25px;
        padding-bottom: 5px;
    }

    /* Indian Railways Blue Header Box */
    .header-container {
        background-color: #003366;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 5px solid #ffcc00;
        margin-bottom: 30px;
        text-align: center;
    }

    /* Buttons */
    .stButton>button {
        background-color: #ffcc00;
        color: #000000;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
        height: 3em;
        font-size: 1.1rem;
    }
    
    /* Dropdown Arrow Visibility */
    svg[title="open"] { fill: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN INTERFACE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Indian_Railways_NS_Logo.svg/1200px-Indian_Railways_NS_Logo.svg.png", width=120)
        st.markdown("<h1 style='text-align: center; color: #ffcc00;'>SYSTEM LOGIN</h1>", unsafe_allow_html=True)
        login_id = st.text_input("Enter Password (HRMS ID)", type="password").upper().strip()
        if st.button("ENTER"):
            clean_login = re.sub(r'[^A-
