import streamlit as st
from fpdf import FPDF
import re

# --- 1. SEPARATE MAPPING LOGIC (Easy to edit) ---
# You can change these lists anytime without touching the UI code
OFFICE_MAPPINGS = {
    "पद (Designations)": ["SSE", "JE", "Technician-I", "Technician-II", "Helper", "Other"],
    
    "ट्रेड (Trades)": ["Fitter", "Welder", "Painter", "Machinist", "Carpenter", "Electrician"],
    
    "समस्या के प्रकार (Grievance Types)": [
        "Salary Dispute", 
        "Leave/Pass Issue", 
        "Quarter Allotment", 
        "Safety Equipment", 
        "Other"
    ],
    
    "संबंधित अधिकारी (Redressal Y)": [
        "WM (Workshop Manager)", 
        "AWM (Asst. Workshop Manager)", 
        "Dy.CME", 
        "SPO (Senior Personnel Officer)"
    ],
    
    "जारी करने वाला (Issuing Z)": [
        "Ch.OS", 
        "SSE In-charge", 
        "Establishment Section", 
        "Admin Branch"
    ]
}

# --- 2. USER REGISTRY ---
AUTHORIZED_USERS = {
    "HRMS01": "Amit Kumar",
    "CWA123": "Suresh Sharma",
    "ADMIN1": "Rajesh Singh"
}

# --- 3. CONFIGURATION & CSS ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    .login-container { display: flex; justify-content: center; align-items: center; height: 50vh; }
    .employee-box {
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #1f4e79;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .stButton>button { background-color: #1f4e79; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<h1 style='text-align: center; color: #1f4e79;'>LOGIN</h1>", unsafe_allow_html=True)
        login_id = st.text_input("Enter Password", type="password").upper()
        if st.button("ENTER"):
            if login_id in AUTHORIZED_USERS:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = AUTHORIZED_USERS[login_id]
                st.rerun()
            else:
                st.error("Access Denied: Invalid HRMS ID")
    st.stop()

# --- 5. MAIN FORM INTERFACE ---
st.markdown(f"<p style='text-align: right; color: gray;'>नमस्ते, <b>{st.session_state['user_name']}</b></p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>🛠️ कैरिज वर्कशॉप आलमाग Grievance Redressal System</h2>", unsafe_allow_html=True)

with st.form("cwa_form"):
    # Group: Initial Employee Details
    st.markdown("### 📋 कर्मचारी का विवरण (Employee Details)")
    with st.container():
        st.markdown('<div class="employee-box">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            emp_name = st.text_input("कर्मचारी का नाम")
            emp_desig = st.selectbox("कर्मचारी का पद", OFFICE_MAPPINGS["पद (Designations)"])
            emp_trade = st.selectbox("कर्मचारी का ट्रेड", OFFICE_MAPPINGS["ट्रेड (Trades)"])
        with c2:
            emp_no = st.text_input("कर्मचारी का Employee Number")
            hrms_id = st.text_input("कर्मचारी की HRMS ID (6 Capital Letters)", max_chars=6).upper()
            section = st.text_input("कर्मचारी का सेक्शन")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Group: Grievance & Authorities
    st.markdown("### 📝 समस्या एवं अधिकारी (Grievance & Authorities)")
    col_a, col_b = st.columns(2)
    with col_a:
        g_type = st.selectbox("समस्या का प्रकार", OFFICE_MAPPINGS["समस्या के प्रकार (Grievance Types)"])
        auth_y = st.selectbox("संबंधित अधिकारी (Y)", OFFICE_MAPPINGS["संबंधित अधिकारी (Redressal Y)"])
    with col_b:
        date_c = st.date_input("दिनांक")
        auth_z = st.selectbox("पत्र जारी करने हेतु अधिकारी (Z)", OFFICE_MAPPINGS["जारी करने वाला (Issuing Z)"])
    
    g_detail = st.text_area("कर्मचारी की समस्या का विवरण (Main Grievance Detail)")

    submit = st.form_submit_button("GENERATE FORMAL PDF")

# --- 6. PDF GENERATION WITH UTSAAH.TTF ---
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Registering the Hindi Font
    # Ensure utsaah.ttf is in the same folder as app.py
    try:
        pdf.add_font('Utsaah', '', 'utsaah.ttf', uni=True)
        pdf.set_font('Utsaah', '', 14)
    except:
        pdf.set_font('Arial', '', 12) # Fallback if font fails

    pdf.cell(200, 10, "कैरिज वर्कशॉप आलमाग - ग्रीवांस विवरण", ln=True, align='C')
    pdf.ln(10)
    
    # Adding data to PDF
    content = [
        f"दिनांक: {data['date']}",
        f"कर्मचारी का नाम: {data['name']}",
        f"पद/ट्रेड: {data['desig']} / {data['trade']}",
        f"HRMS ID: {data['hrms']}",
        f"समस्या: {data['type']}",
        f"विवरण: {data['detail']}",
        f"\nसंबंधित अधिकारी: {data['y']}",
        f"जारीकर्ता: {data['z']}",
        f"\nलॉगिन कर्ता: {st.session_state['user_name']}"
    ]
    
    for line in content:
        pdf.multi_cell(0, 10, line)
    
    return pdf.output(dest='S').encode('latin-1')

if submit:
    if not re.match(r"^[A-Z]{6}$", hrms_id):
        st.error("HRMS ID must be exactly 6 capital letters.")
    else:
        pdf_output = create_pdf({
            "date": str(date_c), "name": emp_name, "desig": emp_desig,
            "trade": emp_trade, "hrms": hrms_id, "type": g_type,
            "detail": g_detail, "y": auth_y, "z": auth_z
        })
        st.success("PDF Generated Successfully!")
        st.download_button("Download Letter", pdf_output, f"Grievance_{hrms_id}.pdf", "application/pdf")
