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

# --- 2. ENTERPRISE GREY THEME ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #273342; color: #e2e8f0; }
    .login-credentials-label { font-size: 1.5rem !important; color: #60a5fa; font-weight: bold; }
    label { color: #60a5fa !important; font-weight: 700 !important; font-size: 1.5rem !important; }
    .welcome-text { font-size: 2.5rem !important; color: #3b82f6 !important; font-weight: 800; margin-bottom: 20px; }
    .section-header { color: #ffffff; font-size: 2.2rem; font-weight: 800; border-bottom: 3px solid #3b82f6; margin-top: 30px; margin-bottom: 20px; }
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #ffffff !important; color: #1e293b !important;
        border: 2px solid #3b82f6 !important; border-radius: 6px !important;
    }
    svg[title="open"] { fill: #3b82f6 !important; transform: scale(1.5); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN INTERFACE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([0.5, 1.2, 0.5])
    with col_mid:
        if os.path.exists("banner.png"):
            st.image("banner.png", use_container_width=True)
        st.markdown("<h1 style='text-align: center; color: white;'>LOGIN</h1>", unsafe_allow_html=True)
        st.markdown('<p class="login-credentials-label">Enter Login Credentials</p>', unsafe_allow_html=True)
        login_id = st.text_input("", type="password", label_visibility="collapsed").upper().strip()
        if st.button("ENTER"):
            clean_login = re.sub(r'[^A-Z0-9]', '', login_id)
            if clean_login in data["USERS"]:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = data["USERS"][clean_login]
                st.rerun()
            else: st.error("Invalid Credentials")
    st.stop()
