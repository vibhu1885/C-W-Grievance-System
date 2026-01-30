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
    # 'utf-8-sig' automatically removes invisible BOM characters from the start of the file
    with open("data.txt", "r", encoding="utf-8-sig") as f:
        for line in f:
            # .strip() removes spaces AND hidden newline characters (\n, \r)
            clean_line = line.strip() 
            if not clean_line: continue
            
            # Detect Headers - use .upper() to be safe
            header_check = clean_line.upper()
            if header_check == "USER_LIST": current_section = "USERS"
            elif header_check == "DESIGNATIONS": current_section = "DESIG"
            elif header_check == "TRADES": current_section = "TRADE"
            elif header_check == "GRIEVANCE_TYPES": current_section = "G_TYPE"
            elif header_check == "AUTHORITIES_Y": current_section = "AUTH_Y"
            elif header_check == "AUTHORITIES_Z": current_section = "AUTH_Z"
            
            elif current_section == "USERS":
                if "," in clean_line:
                    uid, uname = clean_line.split(",", 1)
                    # We use .strip() on both to be 100% sure
                    data_map["USERS"][uid.strip().upper()] = uname.strip()
            elif current_section:
                data_map[current_section].append(clean_line)
                
    return data_map

data = load_custom_data()

# --- 2. UI CONFIG & BEAUTIFICATION ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        background-color: #1f4e79; 
        color: white; 
        font-weight: bold; 
        width: 100%; 
        border-radius: 8px; 
        height: 3em; 
    }
    .employee-box { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 10px solid #1f4e79; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #1f4e79; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<br><br><h1 style='text-align: center;'>LOGIN</h1>", unsafe_allow_html=True)
        login_id = st.text_input("Enter Password", type="password").upper()
        if st.button("ENTER"):
            if login_id in data["USERS"]:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = data["USERS"][login_id]
                st.rerun()
            else:
                st.error("Access Denied: Invalid HRMS ID")
    st.stop()

# --- 4. PDF GENERATION LOGIC ---
def create_pdf(form_data, user):
    pdf = FPDF()
    pdf.add_page()
    
    # Load Hindi Font
    font_path = "utsaah.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Utsaah', '', font_path, uni=True)
        pdf.set_font('Utsaah', '', 16)
    else:
        pdf.set_font('Arial', 'B', 16)

    # Header
    pdf.cell(200, 10, "कैरिज वर्कशॉप आलमाग - ग्रीवांस विवरण", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font('Utsaah' if os.path.exists(font_path) else 'Arial', '', 12)
    
    lines = [
        f"दिनांक: {form_data['date']}",
        f"कर्मचारी का नाम: {form_data['name']}",
        f"पद: {form_data['desig']} | ट्रेड: {form_data['trade']}",
        f"कर्मचारी संख्या: {form_data['emp_no']} | HRMS ID: {form_data['hrms']}",
        f"सेक्शन: {form_data['section']}",
        f"\nसमस्या का प्रकार: {form_data['type']}",
        f"समस्या का विवरण: {form_data['detail']}",
        f"\nसंबंधित अधिकारी (Y): {form_data['y']}",
        f"पत्र जारी करने हेतु अधिकारी (Z): {form_data['z']}",
        f"\nग्रीवांस दर्ज करने वाला: {user}"
    ]
    
    for line in lines:
        pdf.multi_cell(0, 10, line)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 5. MAIN INTERFACE ---
col_head, col_logout = st.columns([0.85, 0.15])
with col_head:
    st.markdown(f"### नमस्ते, **{st.session_state['user_name']}** 👋")
with col_logout:
    if st.button("LOGOUT"):
        st.session_state["authenticated"] = False
        st.rerun()

st.markdown("<h2 style='text-align: center;'>🛠️ कैरिज वर्कशॉप आलमाग Grievance Redressal System</h2>", unsafe_allow_html=True)

with st.form("main_form"):
    # Section: Initial Employee Details
    st.markdown("### 📋 कर्मचारी का विवरण (Initial Employee Details)")
    with st.container():
        st.markdown('<div class="employee-box">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            emp_name = st.text_input("कर्मचारी का नाम")
            emp_desig = st.selectbox("कर्मचारी का पद", data["DESIG"])
            emp_trade = st.selectbox("कर्मचारी का ट्रेड", data["TRADE"])
        with c2:
            emp_no = st.text_input("Employee Number")
            hrms_id = st.text_input("Employee HRMS ID", max_chars=6).upper()
            section = st.text_input("सेक्शन")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📝 समस्या विवरण")
    col_a, col_b = st.columns(2)
    with col_a:
        g_type = st.selectbox("समस्या प्रकार", data["G_TYPE"])
        auth_y = st.selectbox("संबंधित अधिकारी (Y)", data["AUTH_Y"])
    with col_b:
        date_c = st.date_input("दिनांक")
        auth_z = st.selectbox("जारीकर्ता (Z)", data["AUTH_Z"])
    
    g_detail = st.text_area("विवरण (Detailed Grievance)")
    
    st.info(f"दर्जकर्ता: {st.session_state['user_name']}")
    
    if st.form_submit_button("GENERATE FORMAL PDF"):
        if not re.match(r"^[A-Z]{6}$", hrms_id):
            st.error("❌ HRMS ID must be exactly 6 CAPITAL letters.")
        elif not emp_name or not g_detail:
            st.warning("⚠️ Please fill Name and Grievance Details.")
        else:
            final_data = {
                "date": date_c.strftime("%d-%m-%Y"),
                "name": emp_name, "desig": emp_desig, "trade": emp_trade,
                "emp_no": emp_no, "hrms": hrms_id, "section": section,
                "type": g_type, "detail": g_detail, "y": auth_y, "z": auth_z
            }
            pdf_bytes = create_pdf(final_data, st.session_state['user_name'])
            st.success("✅ PDF Generated!")
            st.download_button("Download Letter", pdf_bytes, f"Grievance_{hrms_id}.pdf", "application/pdf")

