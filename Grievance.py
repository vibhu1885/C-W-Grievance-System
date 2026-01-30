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
    /* Professional Slate Grey Background */
    .stApp {
        background-color: #273342;
        color: #e2e8f0;
    }
    
    /* Input Field Labels - High Visibility but Softer than Gold */
    label {
        color: #60a5fa !important; /* Soft Blue */
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-bottom: 8px !important;
    }

    /* Polished Dropdowns & Text Boxes */
    /* We force a white background and a distinct border for the 'Dropdown' look */
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 6px !important;
        min-height: 45px;
    }

    /* Styling the Dropdown Arrow to look like a Button */
    svg[title="open"] { 
        fill: #3b82f6 !important; 
        transform: scale(1.2);
    }

    /* Section Headers */
    .section-header {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 800;
        border-bottom: 2px solid #60a5fa;
        margin-top: 25px;
        margin-bottom: 15px;
        padding-bottom: 5px;
    }

    /* Header Banner */
    .banner {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border-bottom: 4px solid #3b82f6;
        margin-bottom: 25px;
    }

    /* Submit Button */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 3.2em;
        width: 100%;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN INTERFACE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Indian_Railways_NS_Logo.svg/1200px-Indian_Railways_NS_Logo.svg.png", width=100)
        st.markdown("<h2 style='text-align: center; color: white;'>OFFICER LOGIN</h2>", unsafe_allow_html=True)
        login_id = st.text_input("Enter Password", type="password").upper().strip()
        if st.button("LOGIN"):
            clean_login = re.sub(r'[^A-Z0-9]', '', login_id)
            if clean_login in data["USERS"]:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = data["USERS"][clean_login]
                st.rerun()
            else:
                st.error("Invalid ID")
    st.stop()

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="banner">', unsafe_allow_html=True)
b_logo, b_title = st.columns([0.1, 0.9])
with b_logo:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Indian_Railways_NS_Logo.svg/1200px-Indian_Railways_NS_Logo.svg.png", width=80)
with b_title:
    st.markdown("<h2 style='color: white; margin:0;'>कैरिज वर्कशॉप आलमाग (CWA)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #60a5fa; margin:0; font-size: 1.2rem;'>Grievance Redressal Management System</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Welcome Bar
c_greet, c_out = st.columns([0.8, 0.2])
with c_greet:
    st.markdown(f"Welcome, **{st.session_state['user_name']}**")
with c_out:
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

with st.form("main_form"):
    # Section 1: Employee Details
    st.markdown('<div class="section-header">📋 कर्मचारी का विवरण (Employee details)</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        emp_name = st.text_input("1. कर्मचारी का नाम")
        emp_desig = st.selectbox("2. कर्मचारी का पद", data["DESIG"])
        emp_trade = st.selectbox("3. कर्मचारी का ट्रेड", data["TRADE"])
    with col2:
        emp_no = st.text_input("4. Employee Number")
        hrms_id = st.text_input("5. HRMS ID", max_chars=6).upper()
        section = st.text_input("6. सेक्शन")

    # Section 2: Grievance Details
    st.markdown('<div class="section-header">📝 समस्या विवरण (Grievance)</div>', unsafe_allow_html=True)
    
    gx, gy = st.columns(2)
    with gx:
        g_type = st.selectbox("Grievance प्रकार", data["G_TYPE"])
        auth_y = st.selectbox("संबंधित अधिकारी (Letter To)", data["AUTH_Y"])
    with gy:
        date_c = st.date_input("Grievance दिनांक")
        auth_z = st.selectbox("पत्र जारीकर्ता अधिकारी (Letter By)", data["AUTH_Z"])
    
    g_detail = st.text_area("विवरण (Detailed Grievance)")

    st.write(f"✍️ **Officer Registering:** {st.session_state['user_name']}")
    
    _, btn_c, _ = st.columns([1, 1, 1])
    with btn_c:
        submit = st.form_submit_button("📜 GENERATE PDF")

if submit:
    # PDF Logic (utsaah.ttf required in repo)
    st.success("Form submitted successfully.")
