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

# --- 2. VIBRANT COLORFUL THEME WITH WHITE TEXT BOXES ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #0d9488 100%);
    }
    
    /* Global Text Styling */
    html, body, [class*="st-"] {
        font-size: 1.1rem;
    }

    /* Input Field Labels - Bigger & Darker */
    label {
        color: #1e293b !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        margin-bottom: 8px !important;
    }

    /* Force White Text Boxes */
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* White Box Sections */
    .white-section {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        border-top: 10px solid #f59e0b;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px rgba(0,0,0,0.2);
    }

    /* Headings Styling */
    .big-heading {
        color: #ffffff;
        font-size: 3rem;
        font-weight: 900;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        text-align: center;
        margin-bottom: 30px;
    }
    
    .section-header {
        color: #1e3a8a;
        font-size: 1.8rem;
        font-weight: 900;
        margin-bottom: 20px;
        text-decoration: underline;
    }

    /* Button */
    .stButton>button {
        background-color: #f59e0b;
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: bold;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
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
        with st.container():
            st.markdown("<h1 style='text-align: center; color: white;'>SYSTEM LOGIN</h1>", unsafe_allow_html=True)
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
    st.markdown(f"<h3 style='color: #e0f2fe;'>Welcome, {st.session_state['user_name']} 👋</h3>", unsafe_allow_html=True)
with col_out:
    if st.button("LOGOUT"):
        st.session_state["authenticated"] = False
        st.rerun()

st.markdown("<h1 class='big-heading'>🛠️ कैरिज वर्कशॉप आलमाग Grievance System</h1>", unsafe_allow_html=True)

with st.form("main_form"):
    # Group 1: Employee Details (Chronology Updated)
    st.markdown('<p class="section-header">📋 कर्मचारी का विवरण (Employee details)</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="white-section">', unsafe_allow_html=True)
        # Row 1
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            emp_name = st.text_input("कर्मचारी का नाम")
        with r1_c2:
            emp_desig = st.selectbox("कर्मचारी का पद", data["DESIG"])
        
        # Row 2
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            emp_trade = st.selectbox("कर्मचारी का ट्रेड", data["TRADE"])
        with r2_c2:
            emp_no = st.text_input("Employee Number")
        
        # Row 3
        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            hrms_id = st.text_input("HRMS ID", max_chars=6).upper()
        with r3_c2:
            section = st.text_input("सेक्शन")
        st.markdown('</div>', unsafe_allow_html=True)

    # Group 2: Grievance Details
    st.markdown('<p class="section-header">📝 समस्या विवरण (Grievance)</p>', unsafe_allow_html=True)
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
    
    st.markdown(f"<p style='color: white; font-size: 1.2rem;'><b>Registering User:</b> {st.session_state['user_name']}</p>", unsafe_allow_html=True)
    
    if st.form_submit_button("GENERATE FORMAL PDF"):
        # PDF logic follows...
        st.success("Creating PDF...")
