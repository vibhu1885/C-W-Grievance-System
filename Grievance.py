import streamlit as st
from fpdf import FPDF
import pandas as pd
import re

# --- 1. DATA FETCHING LOGIC (FROM EXCEL) ---
@st.cache_data
def load_all_data():
    try:
        # Reading the Excel file
        # Make sure your Excel has a 'Users' sheet or columns for these
        df_mappings = pd.read_excel("mappings.xlsx", sheet_name="Mappings") # Dropdowns
        df_users = pd.read_excel("mappings.xlsx", sheet_name="Users")      # Auth Users
        
        return {
            "desig": df_mappings["Designations"].dropna().tolist(),
            "trade": df_mappings["Trades"].dropna().tolist(),
            "g_type": df_mappings["GrievanceTypes"].dropna().tolist(),
            "auth_y": df_mappings["AuthoritiesY"].dropna().tolist(),
            "auth_z": df_mappings["AuthoritiesZ"].dropna().tolist(),
            "users": dict(zip(df_users["UserID"].str.upper(), df_users["UserName"]))
        }
    except Exception as e:
        st.error(f"Error loading Excel data: {e}. Please check sheet names and columns.")
        return None

data = load_all_data()

# --- 2. CONFIGURATION & CSS ---
st.set_page_config(page_title="CWA Grievance System", layout="wide")

st.markdown("""
    <style>
    .login-container { text-align: center; padding: 50px; }
    .employee-box {
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #1f4e79;
        margin-bottom: 20px;
    }
    .stButton>button { background-color: #1f4e79; color: white; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<h1 style='text-align: center;'>LOGIN</h1>", unsafe_allow_html=True)
        login_id = st.text_input("Enter Password", type="password").upper()
        if st.button("ENTER"):
            if data and login_id in data["users"]:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = data["users"][login_id]
                st.rerun()
            else:
                st.error("Access Denied: Invalid HRMS ID")
    st.stop()

# --- 4. MAIN FORM INTERFACE ---
st.markdown(f"<p style='text-align: right;'>नमस्ते, <b>{st.session_state['user_name']}</b></p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>🛠️ कैरिज वर्कशॉप आलमाग Grievance Redressal System</h2>", unsafe_allow_html=True)

if data:
    with st.form("cwa_form"):
        # GROUP: Initial Employee Details
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

        # GROUP: Grievance Details
        st.markdown("### 📝 समस्या एवं अधिकारी")
        col_a, col_b = st.columns(2)
        with col_a:
            g_type = st.selectbox("समस्या का प्रकार", data["g_type"])
            auth_y = st.selectbox("संबंधित अधिकारी (Y)", data["auth_y"])
        with col_b:
            date_c = st.date_input("दिनांक")
            auth_z = st.selectbox("पत्र जारी करने हेतु अधिकारी (Z)", data["auth_z"])
        
        g_detail = st.text_area("कर्मचारी की समस्या का विवरण")

        # Automatically logged-in user name
        st.info(f"ग्रीवांस दर्ज करने वाला कर्मचारी/अधिकारी: {st.session_state['user_name']}")

        submit = st.form_submit_button("GENERATE FORMAL PDF")

    if submit:
        # Regular expression for 6 Capital Letters
        if not re.match(r"^[A-Z]{6}$", hrms_id):
            st.error("HRMS ID must be exactly 6 CAPITAL letters.")
        else:
            st.success(f"Grievance logged by {st.session_state['user_name']}")
            # PDF Generation code...
