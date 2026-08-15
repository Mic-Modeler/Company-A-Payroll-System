import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="DTR & Attendance System", layout="centered")

# 2. Simple Login Credentials (Pwede mong palitan)
USER_CREDENTIALS = {"admin": "1234", "staff": "pass123"}

# Initialize session states
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ---------------- LOGIN SCREEN ----------------
if not st.session_state["logged_in"]:
    st.title("🔒 System Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Maling Username o Password!")

# ---------------- MAIN APP (Pagkatapos mag-login) ----------------
else:
    # Logout Button sa Sidebar
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    # Live Clock Setup (Awtomatikong magre-refresh bawat 1 segundo)
    st_autorefresh(interval=1000, key="clock_counter")
    now = datetime.now()
    
    # Header & Live Clock sa Taas
    st.title("⏱️ Attendance & Time-In System")
    st.subheader(f"📅 Today: {now.strftime('%B %d, %Y')} | 🕒 Time: {now.strftime('%I:%M:%S %p')}")
    st.markdown("---")

    # Sample Database ng Employees
    employees = {
        "101": "Juan Dela Cruz",
        "102": "Maria Clara",
        "103": "Jose Rizal"
    }

    # ID Number Input
    st.write("### Employee Time In / Time Out")
    id_input = st.text_input("Enter ID Number:", placeholder="e.g. 101")

    # Kapag tinype ang ID Number, lalabas ang Pangalan
    if id_input:
        if id_input in employees:
            emp_name = employees[id_input]
            st.success(f"👤 **Employee Name:** {emp_name}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🟢 TIME IN", use_container_width=True):
                    current_time = datetime.now().strftime("%I:%M:%S %p")
                    st.info(f"✅ Time In Success for **{emp_name}** at {current_time}")
            
            with col2:
                if st.button("🔴 TIME OUT", use_container_width=True):
                    current_time = datetime.now().strftime("%I:%M:%S %p")
                    st.warning(f"🔴 Time Out Success for **{emp_name}** at {current_time}")
        else:
            st.error("❌ ID Number Not Found!")
