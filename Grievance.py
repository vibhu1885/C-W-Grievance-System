import streamlit as st
from fpdf import FPDF
import re

# --- USER REGISTRY (Authorized Employees) ---
# Map HRMS ID to the Name of the person logging the grievance
AUTHORIZED_USERS = {
    "OAIFHL": "Vibhore Maurya, Sr. Clerk",
    "FHBODA": "Vivek Kumar Dubey, SWLI",
    
}

# --- CONFIGURATION ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

# --- AUTHENTICATION LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_name"] = ""

if not st.session_state["authenticated"]:
    st.title("🔐 लॉगिन करें")
    login_id = st.text_input("अपनी HRMS ID दर्ज करें (Password)", type="password").upper()
    if st.button("प्रवेश करें"):
        if login_id in AUTHORIZED_USERS:
            st.session_state["authenticated"] = True
            st.session_state["user_name"] = AUTHORIZED_USERS[login_id]
            st.rerun()
        else:
            st.error("अमान्य HRMS ID। कृपया सही आईडी दर्ज करें।")
    st.stop()

# --- MAIN APP INTERFACE ---
st.markdown(f"### नमस्ते, **{st.session_state['user_name']}** 👋")
st.title("🛠️ कैरिज वर्कशॉप आलमाग Grievance Redressal System")
st.divider()

with st.form("main_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("दिनांक")
        emp_name = st.text_input("कर्मचारी का नाम")
        emp_desig = st.selectbox("कर्मचारी का पद", ["SSE", "JE", "Technician-I", "Technician-II", "Helper"])
        emp_trade = st.selectbox("कर्मचारी का ट्रेड", ["Fitter", "Welder", "Painter", "Machinist", "Carpenter"])
        emp_no = st.text_input("कर्मचारी का Employee Number")

    with col2:
        hrms_id = st.text_input("कर्मचारी की HRMS ID (6 Capital Letters)", max_chars=6).upper()
        section = st.text_input("कर्मचारी का सेक्शन")
        g_type = st.selectbox("कर्मचारी की समस्या का प्रकार", ["Salary", "Leave", "Pass/PTO", "Quarters", "Other"])
        authority_y = st.selectbox("संबंधित अधिकारी", ["WM", "AWM", "Dy.CME", "SPO"])
        authority_z = st.selectbox("पत्र जारी करने हेतु अधिकारी", ["Ch.OS", "SSE In-charge", "Establishment Section"])

    g_detail = st.text_area("कर्मचारी की समस्या का विवरण (Main Grievance)")
    
    # Static info for the logger
    st.write(f"**ग्रीवांस दर्ज करने वाला कर्मचारी/अधिकारी:** {st.session_state['user_name']}")

    submit = st.form_submit_button("PDF जेनरेट करें")

# --- VALIDATION & PDF GENERATION ---
if submit:
    # Check HRMS ID format: Exactly 6 Capital Letters
    if not re.match(r"^[A-Z]{6}$", hrms_id):
        st.error("त्रुटि: कर्मचारी की HRMS ID ठीक 6 कैपिटल लेटर्स की होनी चाहिए (उदा: ABCDEF)।")
    elif not emp_name or not g_detail:
        st.warning("कृपया सभी अनिवार्य जानकारी भरें।")
    else:
        st.success("डेटा सत्यापित! PDF तैयार की जा रही है...")
        # (PDF generation logic would go here - similar to previous version but with Hindi headers)
