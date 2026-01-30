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
        # 'utf-8-sig' handles invisible BOM marks from Windows text files
        with open("data.txt", "r", encoding="utf-8-sig") as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line: continue
                
                # Header Detection
                if clean_line == "USER_LIST": current_section = "USERS"
                elif clean_line == "DESIGNATIONS": current_section = "DESIG"
                elif clean_line == "TRADES": current_section = "TRADE"
                elif clean_line == "GRIEVANCE_TYPES": current_section = "G_TYPE"
                elif clean_line == "AUTHORITIES_Y": current_section = "AUTH_Y"
                elif clean_line == "AUTHORITIES_Z": current_section = "AUTH_Z"
                
                elif current_section == "USERS":
                    if "," in clean_line:
                        uid, uname = clean_line.split(",", 1)
                        # Clean ID: Keep only alphanumeric, no spaces or hidden marks
                        fixed_uid = re.sub(r'[^a-zA-Z0-9]', '', uid).upper()
                        data_map["USERS"][fixed_uid] = uname.strip()
                elif current_section:
                    data_map[current_section].append(clean_line)
    except Exception as e:
        st.error(f"Error loading data.txt: {e}")
                
    return data_map

data = load_custom_data()

# --- 2. THEME & BEAUTIFICATION (Vibrant Light Theme) ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    /* Background and global settings */
    .stApp {
        background-color: #f0f4f8;
    }
    /* Buttons */
    .stButton>button { 
        background-color: #007bff; 
        color: white; 
        border-radius: 8px; 
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border-color: #0056b3;
    }
    /* Employee Details Box */
    .employee-box { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 8px solid #007bff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 0px !important; /* Removes the white strip gap */
    }
    /* Headers */
    .section-header {
        color: #2c3e50;
        font-size: 1.1rem;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<br><br><h1 style
