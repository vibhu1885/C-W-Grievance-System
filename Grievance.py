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
        # utf-8-sig handles the invisible BOM character at the start of files
        with open("data.txt", "r", encoding="utf-8-sig") as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line: continue
                
                # Header Detection (Must be exact match)
                if clean_line == "USER_LIST": current_section = "USERS"
                elif clean_line == "DESIGNATIONS": current_section = "DESIG"
                elif clean_line == "TRADES": current_section = "TRADE"
                elif clean_line == "GRIEVANCE_TYPES": current_section = "G_TYPE"
                elif clean_line == "AUTHORITIES_Y": current_section = "AUTH_Y"
                elif clean_line == "AUTHORITIES_Z": current_section = "AUTH_Z"
                
                elif current_section == "USERS":
                    if "," in clean_line:
                        uid, uname = clean_line.split(",", 1)
                        # Clean ID: removes any hidden special characters
                        fixed_uid = re.sub(r'[^a-zA-Z0-9]', '', uid).upper()
                        data_map["USERS"][fixed_uid] = uname.strip()
                elif current_section:
                    data_map[current_section].append(clean_line)
    except Exception as e:
        st.error(f"Error reading data.txt: {e}")
                
    return data_map

data = load_custom_data()

# --- 2. THEME & BEAUTIFICATION ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    .stButton>button { 
        background-color: #007bff; color: white; border-radius: 8px; font-weight: bold; width: 100%;
    }
    .employee-box { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 8px solid #007bff; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 0px !important; 
    }
    .section-header {
        color: #2c3e50; font-size: 1.1rem; font-weight: bold; margin-top: 15px; margin-bottom: 5px;
    }
    /* Removes extra white space under the container */
    [data-testid="stVerticalBlock"] > div:nth-child(2) { margin-top: -15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<br><br><h1 style='text-align: center; color: #007bff;'>LOGIN</h1>", unsafe_allow_html=True)
        login_id = st.text_input("Enter Password", type="password").upper().strip()
        
        if st.button("ENTER"):
            # Deep clean input for comparison
            clean_login = re.sub(r'[^A-Z0-9]', '', login_id)
            if clean_login in data["USERS"]:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = data["USERS"][clean_login]
                st.rerun()
            else:
                st.error("Access Denied: Please check HRMS ID")
    st.stop()

# --- 4. PDF GENERATION FUNCTION ---
def create_pdf(f_data, logger):
    pdf = FPDF()
    pdf.add_page()
    
    font_p = "utsaah.ttf"
    if os.path.exists(font_p):
        pdf.add_font('Utsaah', '', font_p, uni=True)
        pdf.set_font('Utsaah', '', 16)
    else:
        pdf.set_font('Arial', 'B', 16)

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
        f"\nसंबंधित अधिकारी (To): {f_data['y']}",
        f"पत्र जारीकर्ता (By): {f_data['z']}",
        f"\nEmployee/ Officer registering grievance: {logger}"
    ]
    for line in lines:
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest='S').encode('latin-1')

# --- 5. MAIN INTERFACE ---
col_greet, col_out = st.columns([0.8, 0.2])
with col_greet:
    st.markdown(f"#### Welcome, **{st.session_state['user_name']}** 👋")
with col_out:
    if st.button("LOGOUT"):
        st.session_state["authenticated"] = False
        st.rerun()

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>🛠️ कैरिज वर्कशॉप आलमाग Grievance System</h2>", unsafe_allow_html=True)

with st.form("main_form"):
    # Group 1: Employee Details
    st.markdown('<p class="section-header">📋 कर्मचारी का विवरण (Employee details)</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="employee-box">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            emp_name = st.text_input("कर्मचारी का नाम")
            emp_desig = st.selectbox("कर्मचारी का पद", data["DESIG"])
        with c2:
            emp_trade = st.selectbox("कर्मचारी का ट्रेड", data["TRADE"])
            emp_no = st.text_input("Employee Number")
        with c3:
            hrms_id = st.text_input("Employee HRMS ID", max_chars=6).upper()
            section = st.text_input("सेक्शन")
        st.markdown('</div>', unsafe_allow_html=True)

    # Group 2: Grievance Details
    st.markdown('<p class="section-header">📝 समस्या विवरण (Grievance)</p>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        g_type = st.selectbox("Grievance प्रकार", data["G_TYPE"])
        auth_y = st.selectbox("संबंधित अधिकारी (Letter To)", data["AUTH_Y"])
    with col_b:
        date_c = st.date_input("Grievance दिनांक")
        auth_z = st.selectbox("पत्र जारीकर्ता अधिकारी (Letter By)", data["AUTH_Z"])
    
    g_detail = st.text_area("विवरण (Detailed Grievance)")
    
    st.info(f"Employee/ Officer registering grievance: {st.session_state['user_name']}")
    
    if st.form_submit_button("GENERATE FORMAL PDF"):
        if not re.match(r"^[A-Z]{6}$", hrms_id):
            st.error("HRMS ID must be 6 Capital Letters")
        elif not emp_name:
            st.warning("Please enter Name")
        else:
            final_data = {
                "date": date_c.strftime("%d-%m-%Y"),
                "name": emp_name, "desig": emp_desig, "trade": emp_trade,
                "hrms": hrms_id, "section": section, "type": g_type, 
                "detail": g_detail, "y": auth_y, "z": auth_z
            }
            pdf_b = create_pdf(final_data, st.session_state['user_name'])
            st.download_button("Download Grievance Letter", pdf_b, f"Grievance_{hrms_id}.pdf", "application/pdf")
