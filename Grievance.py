import streamlit as st

st.title(Office Grievance & Redressal System)

# 1. Basic Info
col1, col2 = st.columns(2)
with col1
    collector = st.text_input(Collector Name (Person A))
    visit_date = st.date_input(Date of Visit)
with col2
    office_section = st.selectbox(Office Section (B), [Accounts, Admin, IT Support, HR])
    employee_name = st.text_input(Employee Name (D))

# 2. Grievance Selection (X)
grievance_list = [Salary Delay, Equipment Failure, Leave Request Issue, Other]
selected_grievance = st.selectbox(Type of Grievance (X), grievance_list)

custom_grievance = 
if selected_grievance == Other
    custom_grievance = st.text_area(Enter Custom Grievance Details)

# 3. Authorities (Y & Z)
authority_y = st.selectbox(Redressal Authority (Y), [Director, Manager, Section Head])
authority_z = st.selectbox(Issuing Authority (Z), [Registrar, Head Clerk, Admin Officer])

# 4. Generate Button
if st.button(Generate Grievance Letter PDF)
    # This is where we'll add the PDF generation logic
    st.success(fDrafting letter for {employee_name}...)
    st.write(fAuthority {y} will handle the {selected_grievance}.)