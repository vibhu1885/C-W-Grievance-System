import streamlit as st
from fpdf import FPDF
import pandas as pd
import re

# --- 1. DATA FETCHING LOGIC ---
@st.cache_data # This keeps the app fast by not re-reading the file every second
def load_mappings():
    try:
        # Reads the excel file from your GitHub repository
        df = pd.read_excel("mappings.xlsx")
        return {
            "desig": df["Designations"].dropna().tolist(),
            "trade": df["Trades"].dropna().tolist(),
            "g_type": df["GrievanceTypes"].dropna().tolist(),
            "auth_y": df["AuthoritiesY"].dropna().tolist(),
            "auth_z": df["AuthoritiesZ"].dropna().tolist(),
        }
    except Exception as e:
        # Fallback data in case the Excel file has an issue
        st.error(f"Excel Mapping Error: {e}")
        return {
            "desig": ["SSE", "JE", "Helper"],
            "trade": ["Fitter", "Welder"],
            "g_type": ["Salary", "Other"],
            "auth_y": ["WM"],
            "auth_z": ["Ch.OS"]
        }

mappings = load_mappings()

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
    .stButton>button { background-color: #1f4e79; color: white; font-weight: bold; width: 100%; border-radius: 8px; }
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
    st.markdown("### 📋 कर्मचारी का विवरण (Initial Employee Details)")
    with st.container():
        st.markdown('<div class="employee-box">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            emp_name = st.text_input("कर्मचारी का नाम")
            emp_desig = st.selectbox("कर्मचारी का पद", mappings["desig"])
            emp_trade = st.selectbox("कर्मचारी का ट्रेड", mappings["trade"])
        with c2:
            emp_no = st.text_input("कर्मचारी का Employee Number")
            hrms_id = st.text_input("कर्मचारी की HRMS ID", max_chars=6, help="Exactly 6 Capital Letters").upper()
            section = st.text_input("कर्मचारी का सेक्शन")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown("### 📝 समस्या एवं अधिकारी (Grievance Details)")
    col_a, col_b = st.columns(2)
    with col_a:
        g_type = st.selectbox("कर्मचारी की समस्या का प्रकार", mappings["g_type"])
        auth_y = st.selectbox("संबंधित अधिकारी (Y)", mappings["auth_y"])
    with col_b:
        date_c = st.date_input("दिनांक")
        auth_z = st.selectbox("पत्र जारी करने हेतु अधिकारी (Z)", mappings["auth_z"])
    
    g_detail = st.text_area("कर्मचारी की समस्या का विवरण (Main Grievance Detail)")

    submit = st.form_submit_button("GENERATE FORMAL PDF")

# --- 6. VALIDATION & PDF ---
if submit:
    if not re.match(r"^[A-Z]{6}$", hrms_id):
        st.error("❌ कर्मचारी की HRMS ID ठीक 6 कैपिटल लेटर्स की होनी चाहिए।")
    elif not emp_name:
        st.warning("⚠️ कृपया कर्मचारी का नाम दर्ज करें।")
    else:
        st.success("✅ विवरण सफलतापूर्वक दर्ज किया गया।")
        # PDF Generation logic using utsaah.ttf would follow here
