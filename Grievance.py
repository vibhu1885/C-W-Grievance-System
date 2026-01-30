import streamlit as st
from fpdf import FPDF
import re
import os
import io
from datetime import datetime

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

# --- 2. THEME & IMAGE BUTTON CSS ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #273342; color: #e2e8f0; }
    
    /* Font Scaling */
    .login-credentials-label { font-size: 1.5rem !important; color: #60a5fa; font-weight: bold; }
    label { color: #60a5fa !important; font-weight: 700 !important; font-size: 1.5rem !important; }
    .welcome-text { font-size: 2.5rem !important; color: #3b82f6 !important; font-weight: 800; margin-bottom: 20px; }
    .section-header { color: #ffffff; font-size: 2.2rem; font-weight: 800; border-bottom: 3px solid #3b82f6; margin-top: 30px; margin-bottom: 20px; }

    /* Input Styling */
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

# --- 4. PDF GENERATION LOGIC ---
def generate_official_pdf(form_data, user_name):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Logo & Title
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 25)
    
    # Hindi Font Registration
    if os.path.exists("utsaah.ttf"):
        pdf.add_font('Utsaah', '', 'utsaah.ttf', uni=True)
        pdf.set_font('Utsaah', '', 20)
    else:
        pdf.set_font('Arial', 'B', 16)

    pdf.cell(0, 10, "उत्तर रेलवे - कैरिज वर्कशॉप आलमाग", ln=True, align='C')
    pdf.set_font('Utsaah', '', 14) if os.path.exists("utsaah.ttf") else pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, "Grievance Redressal Management System", ln=True, align='C')
    pdf.ln(15)
    
    # Table Content
    content = [
        ("Grievance दिनांक:", form_data['date']),
        ("कर्मचारी का नाम:", form_data['name']),
        ("पद:", form_data['desig']),
        ("ट्रेड:", form_data['trade']),
        ("Employee Number:", form_data['emp_no']),
        ("HRMS ID:", form_data['hrms']),
        ("सेक्शन:", form_data['section']),
        ("-" * 30, ""),
        ("Grievance प्रकार:", form_data['type']),
        ("संबंधित अधिकारी (To):", form_data['y']),
        ("जारीकर्ता अधिकारी (By):", form_data['z']),
        ("\nविवरण:", form_data['detail'])
    ]
    
    for label, val in content:
        pdf.multi_cell(0, 10, f"{label} {val}")
    
    pdf.ln(20)
    pdf.cell(0, 10, f"दर्जकर्ता: {user_name}", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. MAIN INTERFACE ---
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
with col_title:
    st.markdown("<h1 style='color: white; margin-top: 10px;'>कैरिज वर्कशॉप आलमाग (CWA)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #60a5fa; font-size: 1.5rem;'>Grievance Redressal Management System</p>", unsafe_allow_html=True)

st.markdown(f'<p class="welcome-text">Welcome, {st.session_state["user_name"]} 👋</p>', unsafe_allow_html=True)

if st.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

with st.form("main_form"):
    st.markdown('<div class="section-header">📋 कर्मचारी का विवरण (Employee details)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        emp_name = st.text_input("1. कर्मचारी का नाम")
        emp_desig = st.selectbox("2. कर्मचारी का पद", data["DESIG"])
        emp_trade = st.selectbox("3. कर्मचारी का ट्रेड", data["TRADE"])
    with c2:
        emp_no = st.text_input("4. Employee Number")
        hrms_id = st.text_input("5. HRMS ID", max_chars=6).upper()
        section = st.text_input("6. सेक्शन")

    st.markdown('<div class="section-header">📝 समस्या विवरण (Grievance)</div>', unsafe_allow_html=True)
    gx, gy = st.columns(2)
    with gx:
        g_type = st.selectbox("Grievance प्रकार", data["G_TYPE"])
        auth_y = st.selectbox("संबंधित अधिकारी (Letter To)", data["AUTH_Y"])
    with gy:
        date_c = st.date_input("Grievance दिनांक")
        auth_z = st.selectbox("पत्र जारीकर्ता अधिकारी (Letter By)", data["AUTH_Z"])
    
    g_detail = st.text_area("विवरण (Detailed Grievance)")
    
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if os.path.exists("button.png"):
            st.image("button.png", use_container_width=True)
        submit = st.form_submit_button("GENERATE PDF")

if submit:
    if not emp_name or not hrms_id:
        st.error("Please fill Name and HRMS ID")
    else:
        pdf_data = {
            "date": date_c.strftime("%d-%m-%Y"),
            "name": emp_name, "desig": emp_desig, "trade": emp_trade,
            "emp_no": emp_no, "hrms": hrms_id, "section": section,
            "type": g_type, "detail": g_detail, "y": auth_y, "z": auth_z
        }
        pdf_output = generate_official_pdf(pdf_data, st.session_state["user_name"])
        st.download_button("📥 Click Here to Download PDF", pdf_output, f"Grievance_{hrms_id}.pdf", "application/pdf")
