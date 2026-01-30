import streamlit as st
from fpdf import FPDF
import pandas as pd
import re
import os

# --- 1. DATA FETCHING LOGIC (EXCEL & CONFIG) ---
@st.cache_data
def load_all_data():
    try:
        # Load Mappings and Users from Excel
        # Sheet 1: "Mappings", Sheet 2: "Users"
        df_mappings = pd.read_excel("mappings.xlsx", sheet_name="Mappings")
        df_users = pd.read_excel("mappings.xlsx", sheet_name="Users")
        
        return {
            "desig": df_mappings["Designations"].dropna().tolist(),
            "trade": df_mappings["Trades"].dropna().tolist(),
            "g_type": df_mappings["GrievanceTypes"].dropna().tolist(),
            "auth_y": df_mappings["AuthoritiesY"].dropna().tolist(),
            "auth_z": df_mappings["AuthoritiesZ"].dropna().tolist(),
            "users": dict(zip(df_users["UserID"].astype(str).str.upper(), df_users["UserName"]))
        }
    except Exception as e:
        st.error(f"Excel Error: {e}. Please ensure mappings.xlsx has 'Mappings' and 'Users' sheets.")
        return None

data = load_all_data()

# --- 2. CONFIGURATION & BEAUTIFICATION (CSS) ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
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
        border-left: 8px solid #1f4e79;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #1f4e79; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN INTERFACE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<br><br><h1 style='text-align: center;'>LOGIN</h1>", unsafe_allow_html=True)
        login_id = st.text_input("Enter Password", type="password", help="Use your registered HRMS ID").upper()
        if st.button("ENTER"):
            if data and login_id in data["users"]:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = data["users"][login_id]
                st.rerun()
            else:
                st.error("Access Denied: Invalid HRMS ID")
    st.stop()

# --- 4. PDF GENERATION FUNCTION (HINDI SUPPORT) ---
def create_pdf(form_data, logged_in_user):
    pdf = FPDF()
    pdf.add_page()
    
    # Check if font exists, else fallback to Arial
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
    
    # Table-like structure for the letter
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
        f"\nग्रीवांस दर्ज करने वाला: {logged_in_user}"
    ]
    
    for line in lines:
        pdf.multi_cell(0, 10, line)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 5. MAIN FORM ---
st.markdown(f"<p style='text-align: right; color: #555;'>नमस्ते, <b>{st.session_state['user_name']}</b></p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>🛠️ कैरिज वर्कशॉप आलमाग Grievance Redressal System</h2>", unsafe_allow_html=True)

if data:
    with st.form("main_form"):
        # Section 1: Initial Employee Details
        st.markdown("### 📋 कर्मचारी का विवरण (Initial Employee Details)")
        with st.container():
            st.markdown('<div class="employee-box">', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                emp_name = st.text_input("कर्मचारी का नाम")
                emp_desig = st.selectbox("कर्मचारी का पद", data["desig"])
                emp_trade = st.selectbox("कर्मचारी का ट्रेड", data["trade"])
            with c2:
                emp_no = st.text_input("कर्मचारी का Employee Number")
                hrms_id = st.text_input("कर्मचारी की HRMS ID", max_chars=6).upper()
                section = st.text_input("कर्मचारी का सेक्शन")
            st.markdown('</div>', unsafe_allow_html=True)

        # Section 2: Grievance & Authorities
        st.markdown("### 📝 समस्या एवं अधिकारी")
        col_a, col_b = st.columns(2)
        with col_a:
            g_type = st.selectbox("कर्मचारी की समस्या का प्रकार", data["g_type"])
            auth_y = st.selectbox("संबंधित अधिकारी (Y)", data["auth_y"])
        with col_b:
            date_c = st.date_input("दिनांक")
            auth_z = st.selectbox("पत्र जारी करने हेतु अधिकारी (Z)", data["auth_z"])
        
        g_detail = st.text_area("कर्मचारी की समस्या का विवरण (Main Grievance Detail)")

        st.info(f"लॉगिन कर्ता: {st.session_state['user_name']}")
        
        submit = st.form_submit_button("GENERATE FORMAL PDF")

    # --- 6. SUBMISSION & VALIDATION ---
    if submit:
        if not re.match(r"^[A-Z]{6}$", hrms_id):
            st.error("❌ त्रुटि: कर्मचारी की HRMS ID ठीक 6 कैपिटल लेटर्स की होनी चाहिए।")
        elif not emp_name or not g_detail:
            st.warning("⚠️ कृपया कर्मचारी का नाम और समस्या का विवरण भरें।")
        else:
            # Prepare data
            final_data = {
                "date": date_c.strftime("%d-%m-%Y"),
                "name": emp_name, "desig": emp_desig, "trade": emp_trade,
                "emp_no": emp_no, "hrms": hrms_id, "section": section,
                "type": g_type, "detail": g_detail, "y": auth_y, "z": auth_z
            }
            
            # Generate PDF
            try:
                pdf_bytes = create_pdf(final_data, st.session_state['user_name'])
                st.success("✅ PDF सफलतापूर्वक तैयार किया गया!")
                st.download_button(
                    label="Download Grievance Letter",
                    data=pdf_bytes,
                    file_name=f"Grievance_{hrms_id}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF Error: {e}")
