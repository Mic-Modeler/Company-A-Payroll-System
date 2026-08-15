import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime
import pytz
import requests

# 1. Page Configuration
st.set_page_config(page_title="DTR & Attendance System", layout="centered")

# 2. PH Time Zone Setup (GMT+8)
ph_tz = pytz.timezone('Asia/Manila')

# 3. Simple Login Credentials
USER_CREDENTIALS = {"admin": "1234", "staff": "pass123"}

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
            st.rerun()
        else:
            st.error("Maling Username o Password!")

# ---------------- MAIN APP (Pagkatapos mag-login) ----------------
else:
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    # Live Clock Setup (Awtomatikong magre-refresh bawat 1 segundo gamit ang PH Time)
    st_autorefresh(interval=1000, key="clock_counter")
    now_ph = datetime.now(ph_tz)
    
    st.title("⏱️ Attendance & Time-In System")
    st.subheader(f"📅 Today: {now_ph.strftime('%B %d, %Y')} | 🕒 Time: {now_ph.strftime('%I:%M:%S %p')}")
    st.markdown("---")

    # GOOGLE SHEET CONFIGURATION
    SHEET_ID = "19K-XDh-57ml5tblihHjl2dxnF8ArcGIOrJAhwmHy45A"
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Employee%20Database"

    # ⚠️ PALITAN ITO NG IYONG GOOGLE APPS SCRIPT WEB APP URL!
    WEB_APP_URL = "https://script.google.com/macros/s/AKfycbx_YOUR_SCRIPT_ID_HERE/exec"

    # Pagbasa ng Employee Data mula sa Google Sheets
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        
        # Hanapin ang ID at Name columns
        id_col = [c for c in df.columns if 'ID' in c or 'Employee' in c][0]
        name_col = [c for c in df.columns if 'Name' in c][0]
        
        # Gawing text/string ang ID para hindi mawala ang leading zeros (e.g. 001)
        df[id_col] = df[id_col].astype(str).str.zfill(3)
        employees = dict(zip(df[id_col], df[name_col]))
    except Exception as e:
        st.error("⚠️ Hindi mabasa ang Google Sheet. Siguraduhing naka 'Anyone with the link' ang access!")
        employees = {}

    st.write("### Employee Time In / Time Out")
    id_input = st.text_input("Enter ID Number:", placeholder="e.g. 001").strip()

    if id_input:
        # Awtomatikong lalagyan ng leading zero kung '1' lang ang tinype (gagawing '001')
        formatted_id = id_input.zfill(3) if len(id_input) < 3 else id_input
        
        if formatted_id in employees or id_input in employees:
            emp_id = formatted_id if formatted_id in employees else id_input
            emp_name = employees[emp_id]
            
            st.success(f"👤 **Employee Name:** {emp_name}")
            
            col1, col2 = st.columns(2)
            
            # --- TIME IN BUTTON ---
            with col1:
                if st.button("🟢 TIME IN", use_container_width=True):
                    time_str = now_ph.strftime("%I:%M:%S %p")
                    date_str = now_ph.strftime("%Y-%m-%d")
                    
                    payload = {
                        "id": emp_id,
                        "name": emp_name,
                        "date": date_str,
                        "time": time_str,
                        "type": "TIME IN"
                    }
                    try:
                        res = requests.post(WEB_APP_URL, json=payload)
                        st.balloons()
                        st.info(f"✅ **TIME IN** Success for **{emp_name}** at {time_str}")
                    except Exception as err:
                        st.error(f"Failed to auto-sync: {err}")
            
            # --- TIME OUT BUTTON ---
            with col2:
                if st.button("🔴 TIME OUT", use_container_width=True):
                    time_str = now_ph.strftime("%I:%M:%S %p")
                    date_str = now_ph.strftime("%Y-%m-%d")
                    
                    payload = {
                        "id": emp_id,
                        "name": emp_name,
                        "date": date_str,
                        "time": time_str,
                        "type": "TIME OUT"
                    }
                    try:
                        res = requests.post(WEB_APP_URL, json=payload)
                        st.snow()
                        st.warning(f"🔴 **TIME OUT** Success for **{emp_name}** at {time_str}")
                    except Exception as err:
                        st.error(f"Failed to auto-sync: {err}")
        else:
            st.error("❌ ID Number Not Found!")
