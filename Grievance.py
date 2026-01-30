import streamlit as st
from fpdf import FPDF
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

# --- CUSTOM CSS FOR BEAUTIFICATION ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #004b87;
        color: white;
    }
    .login-box {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .employee-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #004b87;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- USER REGISTRY ---
AUTHORIZED_USERS = {
    "HRMS01": "Amit Kumar",
    "ADMINZ": "Rajesh Singh",
    "CWA123": "Suresh Sharma"
}

# --- AUTHENTICATION INTERFACE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Centered Login UI
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<h1 style='text-align: center;'>LOGIN</h1>", unsafe_allow_html=True)
        with st.container():
            login_id = st.text_input("Enter Password", type="password").upper()
            if st.button("ENTER"):
                if login_id in AUTHORIZED_USERS:
                    st.session_state["authenticated"] = True
                    st.session_state["user_name"] = AUTHORIZED_USERS[login_id]
                    st.rerun()
                else:
                    st.error("Invalid Password")
    st.stop()

# --- MAIN APP ---
st.markdown(f"<p style='text-align: right;'>नमस्ते, <b>{st.session_state['user_name']}</b></p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #004b87;'>🛠️ कैरिज वर्कशॉप आलमाग Grievance Redressal System</h2>", unsafe_allow_html=True)
st.divider()

# Form starts here
with st.form("grievance_form"):
    
    # GROUP 1: Initial Employee Details
    st.subheader("📋 कर्मचारी का विवरण (Initial Employee Details)")
    with st.container():
        st.markdown('<div class="employee-box">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            emp_name = st.text_input("कर्मचारी का नाम")
            emp_desig = st.selectbox("कर्मचारी का पद", ["SSE", "JE", "Technician-I", "Technician-II", "Helper"])
        with c2:
            emp_trade = st.selectbox("कर्मचारी का ट्रेड", ["Fitter", "Welder", "Painter", "Machinist", "Carpenter"])
            emp_no = st.text_input("कर्मचारी का Employee Number")
        with c3:
            hrms_id = st.text_input("कर्मचारी की HRMS ID", max_chars=6, help="6 Capital Letters only").upper()
            section = st.text_input("कर्मचारी का सेक्शन")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # GROUP 2: Grievance Details
    st.subheader("📝 समस्या का विवरण (Grievance Details)")
    col_a, col_b = st.columns(2)
    with col_a:
        g_type = st.selectbox("कर्मचारी की समस्या का प्रकार", ["Salary", "Leave", "Pass/PTO", "Quarters", "Other"])
        authority_y = st.selectbox("संबंधित अधिकारी", ["WM", "AWM", "Dy.CME", "SPO"])
    with col_b:
        date = st.date_input("दिनांक")
        authority_z = st.selectbox("पत्र जारी करने हेतु अधिकारी", ["Ch.OS", "SSE In-charge", "Establishment Section"])
    
    g_detail = st.text_area("कर्मचारी की समस्या का विवरण (Main Grievance Text Box)")

    # Submit Button
    submit = st.form_submit_button("GENERATE FORMAL PDF")

# --- VALIDATION LOGIC ---
if submit:
    if not re.match(r"^[A-Z]{6}$", hrms_id):
        st.error("❌ कर्मचारी की HRMS ID ठीक 6 कैपिटल लेटर्स की होनी चाहिए।")
    elif not emp_name:
        st.warning("⚠️ कृपया कर्मचारी का नाम दर्ज करें।")
    else:
        st.success("✅ विवरण सफलतापूर्वक दर्ज किया गया।")
        # PDF logic follows...
