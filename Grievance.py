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
        # utf-8-sig handles invisible characters from Windows text files
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
                
                # Section Content Parsing
                elif current_section == "USERS" and "," in clean_line:
                    uid, uname = clean_line.split(",", 1)
                    data_map["USERS"][uid.strip().upper()] = uname.strip()
                elif current_section:
                    data_map[current_section].append(clean_line)
    except Exception as e:
        st.error(f"Error reading data.txt: {e}")
                
    return data_map

data = load_custom_data()

# --- 2. DARK THEME & HIGH-VISIBILITY CSS ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Input Field Labels - Railway Gold for Visibility */
    label {
        color: #ffcc00 !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        margin-bottom: 5px !important;
    }

    /* Force Pure White Text Boxes for Readable Entry */
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #ffcc00 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* Section Headers with Border */
    .section-header {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 900;
        border-bottom: 4px solid #ffcc00;
        margin-top: 30px;
        margin-bottom: 20px;
        padding-bottom: 5px;
    }

    /* Railway Blue Header Banner */
    .banner {
        background-color: #003366;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 5px solid #ffcc00;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Primary Action Button */
    .stButton>button {
        background-color: #ffcc00;
        color: #000000;
        font-weight: bold;
        border-radius: 10px;
        height: 3.5em;
        font-size: 1.2rem;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #e6b800;
        transform: scale(1.02);
    }
    
    /* Ensure Dropdown Icons are Black against White Background */
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
            # Clean ID for strict matching
            clean_login = re.sub(r'[^A-Z0-9]', '', login_id)
            if clean_login in data["USERS"]:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = data["USERS"][clean_login]
                st.rerun()
            else:
                st.error("Access Denied: Invalid HRMS ID")
    st.stop()

# --- 4. PDF LOGIC (HINDI SUPPORT) ---
def create_pdf(f_data, logger):
    pdf = FPDF()
    pdf.add_page()
    font_p = "utsaah.ttf"
    
    if os.path.exists(font_p):
        pdf.add_font('Utsaah', '', font_p, uni=True)
        pdf.set_font('Utsaah', '', 16)
    else:
        pdf.set_font('Arial', 'B', 16)

    # Header in PDF
    pdf.cell(200, 10, "कैरिज वर्कशॉप आलमाग - ग्रीवांस विवरण", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font('Utsaah' if os.path.exists(font_p) else 'Arial', '', 12)
    
    lines = [
        f"Grievance दिनांक: {f_data['date']}",
        f"नाम: {f_data['name']} ({f_data['hrms']})",
        f"पद/ट्रेड: {f_data['desig']} / {f_data['trade']}",
        f"सेक्शन: {f_data['section']}",
        f"\nGrievance प्रकार: {f_data['type']}",
        f"विवरण: {f_data['detail']}",
        f"\nसंबंधित अधिकारी (Letter To): {f_data['y']}",
        f"पत्र जारीकर्ता अधिकारी (Letter By): {f_data['z']}",
        f"\nEmployee/ Officer registering grievance: {logger}"
    ]
    for line in lines:
        pdf.multi_cell(0, 10, line)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 5. MAIN FORM INTERFACE ---
# Banner
st.markdown('<div class="banner">', unsafe_allow_html=True)
b_logo, b_title = st.columns([0.1, 0.9])
with b_logo:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Indian_Railways_NS_Logo.svg/1200px-Indian_Railways_NS_Logo.svg.png", width=90)
with b_title:
    st.markdown("<h1 style='color: white; margin:0;'>कैरिज वर्कशॉप आलमाग (CWA)</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffcc00; margin:0;'>Grievance Redressal Management System</h3>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# User Info Bar
col_greet, col_out = st.columns([0.8, 0.2])
with col_greet:
    st.markdown(f"### Welcome,:white[{st.session_state['user_name']}] 👋")
with col_out:
    if st.button("🚪 LOGOUT"):
        st.session_state["authenticated"] = False
        st.rerun()

with st.form("main_form"):
    # Section 1: Employee Details (Chronology Fixed)
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
    
    # Generate Button
    _, btn_c, _ = st.columns([1, 1, 1])
    with btn_c:
        submit = st.form_submit_button("📜 GENERATE OFFICIAL PDF")

# Handle Submission
if submit:
    if not re.match(r"^[A-Z]{6}$", hrms_id):
        st.error("HRMS ID must be 6 Capital Letters")
    elif not emp_name:
        st.warning("Please enter Name")
    else:
        # Prepare Data
        pdf_data = {
            "date": date_c.strftime("%d-%m-%Y"),
            "name": emp_name, "desig": emp_desig, "trade": emp_trade,
            "emp_no": emp_no, "hrms": hrms_id, "section": section,
            "type": g_type, "detail": g_detail, "y": auth_y, "z": auth_z
        }
        
        try:
            pdf_bytes = create_pdf(pdf_data, st.session_state['user_name'])
            st.success("PDF Generated Successfully!")
            st.download_button(
                label="📥 Download Official Letter",
                data=pdf_bytes,
                file_name=f"Grievance_{hrms_id}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error creating PDF: {e}")

