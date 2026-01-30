import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Grievance Redressal System", layout="centered")

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "OFFICE GRIEVANCE REDRESSAL LETTER", ln=True, align='C')
    pdf.ln(10)
    
    # Date & Reference
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, f"Date: {data['date']}")
    pdf.cell(100, 10, f"Section: {data['section']}", ln=True, align='R')
    pdf.ln(5)
    
    # Body
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"To: {data['redressal_authority']}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    body_text = (
        f"This is to formally bring to your notice a grievance submitted by "
        f"Mr./Ms. {data['employee_name']} working in the {data['section']} section. "
        f"\n\nGrievance Type: {data['grievance_type']}\n"
        f"Details: {data['details']}\n\n"
        f"This matter was collected during a routine inspection by {data['collector']}. "
        f"We request you to look into this matter for timely redressal."
    )
    pdf.multi_cell(0, 10, body_text)
    pdf.ln(20)
    
    # Signature
    pdf.cell(0, 10, "Regards,", ln=True, align='R')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"{data['issuing_authority']}", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- UI LAYOUT ---
st.header("📋 Grievance Entry Portal")
st.info("Fill the details below to automatically generate a formal letter.")

with st.form("grievance_form"):
    # Section A: Trip Details
    col1, col2 = st.columns(2)
    with col1:
        collector = st.text_input("Collector Name (A)", placeholder="Enter your name")
        visit_date = st.date_input("Date of Visit (C)", value=datetime.now())
    with col2:
        section = st.selectbox("Office Section (B)", ["Accounts", "Admin", "General Store", "IT Cell"])
        emp_name = st.text_input("Employee Name (D)")

    # Section B: The Grievance (X)
    grievance_type = st.selectbox("Grievance Type (X)", 
                                ["Salary Dispute", "Infrastructure Issue", "Workplace Conduct", "Other"])
    
    custom_details = st.text_area("Grievance Details (Dynamic Column)", 
                                 help="Describe the issue in detail here.")

    # Section C: Authorities (Y & Z)
    col3, col4 = st.columns(2)
    with col3:
        redress_auth = st.selectbox("Redressal Authority (Y)", ["Director", "Joint Secretary", "Head of Dept"])
    with col4:
        issue_auth = st.selectbox("Issuing Authority (Z)", ["Registrar", "Admin Officer", "Deputy Director"])

    submit = st.form_submit_button("Generate & Preview Letter")

if submit:
    # Validate inputs
    if not emp_name or not collector:
        st.error("Please fill in the Employee and Collector names.")
    else:
        # Prepare data for PDF
        form_data = {
            "collector": collector,
            "date": visit_date.strftime("%d-%m-%Y"),
            "section": section,
            "employee_name": emp_name,
            "grievance_type": grievance_type,
            "details": custom_details,
            "redressal_authority": redress_auth,
            "issuing_authority": issue_auth
        }
        
        # Generate PDF
        pdf_bytes = generate_pdf(form_data)
        
        st.success("✅ Letter generated successfully!")
        st.download_button(
            label="Download PDF Letter",
            data=pdf_bytes,
            file_name=f"Grievance_{emp_name}.pdf",
            mime="application/pdf"
        )
