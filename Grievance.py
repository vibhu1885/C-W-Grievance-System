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
        st.error("data.txt not found!")
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
                
                elif current_section == "USERS":
                    if "," in clean_line:
                        uid, uname = clean_line.split(",", 1)
                        fixed_uid = re.sub(r'[^a-zA-Z0-9]', '', uid).upper()
                        data_map["USERS"][fixed_uid] = uname.strip()
                elif current_section:
                    data_map[current_section].append(clean_line)
    except Exception as e:
        st.error(f"Error reading data.txt: {e}")
                
    return data_map

data = load_custom_data()

# --- 2. VIBRANT THEME WITH HIGH-VISIBILITY HEADINGS ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #0d9488 100%);
    }
    
    /* Login & Container Styling */
    .stForm {
        background-color: rgba(255, 255, 255, 0.1); /* Transparent layer for glass effect */
        border: none;
    }

    /* Input Field Labels - EXTRA BOLD & VISIBLE */
    label {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 1.3rem !important;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 2px 10px;
        border-radius: 5px;
        display: inline-block;
        margin-bottom: 8px !important;
    }

    /* Force Pure White Text Boxes */
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 3px solid #1e3a8a !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
    }

    /* White Box Sections */
    .white-section {
        background-color: #ffffff;
        padding: 35px;
        border-radius: 15px;
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        margin-bottom: 30px;
    }

    /* Main App Titles - High Visibility */
    .big-heading {
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 900;
        text-shadow: 4px 4px 8px #000000;
        text-align: center;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 40px;
    }
    
    .section-header-box {
        background-color: #f59e0b; /* Bright Amber for section headers */
        color: #ffffff;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 1.8rem;
        font-weight: 900;
        display: inline-block;
        margin-bottom: 15px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.3);
    }

    /* Welcome Text */
    .welcome-bar {
        background-color: #ffffff;
        color: #1e3a8a;
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        border: 2px solid #f59e0b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN INTERFACE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 4px black;'>SYSTEM LOGIN</h1>", unsafe_allow_html=True)
        with st.container():
            login_id = st.text_input("Enter Password (HRMS ID)", type="password").upper().strip()
            if st.button("ENTER SYSTEM"):
                clean_login = re.sub(r'[^A-Z0-9]', '', login_id)
                if clean_login in data["USERS"]:
                    st.session_state["authenticated"] = True
                    st.session_state["user_name"] = data["USERS"][clean_login]
                    st.rerun()
                else:
                    st.error("Invalid HRMS ID")
    st.stop()

# --- 4. MAIN INTERFACE ---
col_greet, col_out = st.columns([0.8, 0.2])
with col_greet:
    st.markdown(f"<div class='welcome-bar'>Welcome, {st.session_state['user_name']} 👋</div>", unsafe_allow_html=True)
with col_out:
    if st.button("LOGOUT"):
        st.session_state["authenticated"] = False
        st.rerun()

st.markdown("<h1 class='big-heading'>🛠️ कैरिज वर्कशॉप आलमाग Grievance System</h1>", unsafe_allow_html=True)

with st.form("main_form"):
    # Group 1: Employee Details (Strict Chronology)
    st.markdown('<div class="section-header-box">📋 कर्मचारी का विवरण (Employee details)</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="white-section">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            emp_name = st.text_input("कर्मचारी का नाम")
            emp_desig = st.selectbox("कर्मचारी का पद", data["DESIG"])
            emp_trade = st.selectbox("कर्मचारी का ट्रेड", data["TRADE"])
        with c2:
            emp_no = st.text_input("Employee Number")
            hrms_id = st.text_input("HRMS ID", max_chars=6).upper()
            section = st.text_input("सेक्शन")
        st.markdown('</div>', unsafe_allow_html=True)

    # Group 2: Grievance Details
    st.markdown('<div class="section-header-box">📝 समस्या विवरण (Grievance)</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="white-section">', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            g_type = st.selectbox("Grievance प्रकार", data["G_TYPE"])
            auth_y = st.selectbox("संबंधित अधिकारी (Letter To)", data["AUTH_Y"])
        with col_b:
            date_c = st.date_input("Grievance दिनांक")
            auth_z = st.selectbox("पत्र जारीकर्ता अधिकारी (Letter By)", data["AUTH_Z"])
        
        g_detail = st.text_area("विवरण (Detailed Grievance)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"<div style='background-color:white; padding:10px; border-radius:10px; display:inline-block;'><b>Registering User:</b> {st.session_state['user_name']}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.form_submit_button("GENERATE FORMAL PDF"):
        # PDF Logic...
        st.success("Creating PDF...")
