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
            emp_desig =
