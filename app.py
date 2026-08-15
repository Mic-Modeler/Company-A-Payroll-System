import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime
import pytz
import requests

st.set_page_config(page_title="DTR & Attendance System", layout="centered")

# PH Time Zone Setup (GMT+8)
ph_tz = pytz.timezone('Asia/Manila')

USER_CREDENTIALS = {"admin": "1234", "staff": "pass123"}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

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

else:
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    # Live Clock Setup (Naka-sync sa PH Time)
    st_autorefresh(interval=1000, key="clock_counter")
    now_ph = datetime.now(ph_tz)
    
    st.title("⏱️ Attendance & Time-In System")
    st.subheader(f"📅 Today: {now_ph.strftime('%B %d, %Y')} | 🕒 Time: {now_ph.strftime('%I:%M:%S %p')}")
    st.markdown("---")

    # GOOGLE SHEET DATA READ LINK
    SHEET_ID = "19K-XDh-57ml5tblihHjl2dxnF8ArcGIOrJAhwmHy45A"
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Employee%20Database"

    # GOOGLE APPS SCRIPT WEB APP URL (I-PASTE DITO ANG NA-COPY MO SA STEP 1)
    WEB_APP_URL = "https://script.google.com/macros/s/AKfycbx_YOUR_SCRIPT_ID_HERE/exec"

    try:
        df = pd.read_csv(SHEET_URL)
        # Inaayos ang ID column name at string formatting
        df.columns = df.columns.str.strip()
        id_col = [c for c in df.columns if 'ID' in c or 'Employee' in c][0]
        name_col = [c for c in df.columns if 'Name' in c][0]
        
        df[id_col] = df[id_col].astype(str).str.zfill(3) # e.g. 001, 002
        employees = dict(zip(df[id_col], df[name_col]))
    except Exception as e:
        st.error("⚠️ Hindi mabasa ang Google Sheet. Siguraduhing Public ('Anyone with the link') ang access.")
        employees = {}

    st.write("### Employee Time In / Time Out")
    id_input = st.text_input("Enter ID Number:", placeholder="e.g. 001").strip()

    if id_input:
        # Format input (halimbawa kung '1' tinype, gagawing '001')
        formatted_id = id_input.zfill(3) if len(id_input) < 3 else id_input
        
        if formatted_id in employees or id_input in employees:
            emp_id = formatted_id if formatted_id in employees else id_input
            emp_name = employees[emp_id]
            
            st.success(f"👤 **Employee Name:** {emp_name}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🟢 TIME IN", use_container_width=True):
                    time_str = now_ph.strftime("%I:%M:%S %p")
                    date_str = now_ph.strftime("%Y-%m-%d")
                    
                    # Auto-sync sa Google Sheets
                    payload = {
                        "id": emp_id,
                        "name": emp_name,
                        "date": date_str,
                        "time": time_str,
                        "type": "TIME IN"
                    }
                    try:
                        requests.post(WEB_APP_URL, json=payload)
                        st.balloons()
                        st.info(f"✅ **TIME IN** Success for **{emp_name}** at {time_str}")
                    except:
                        st.error("May problema sa pag-sync sa Google Sheet.")
            
            with col2:
                if st.button("🔴 TIME OUT", use_container_width=True):
                    time_str = now_ph.strftime("%I:%M:%S %p")
                    date_str = now_ph.strftime("%Y-%m-%d")
                    
                    # Auto-sync sa Google Sheets
                    payload = {
                        "id": emp_id,
                        "name": emp_name,
                        "date": date_str,
                        "time": time_str,
                        "type": "TIME OUT"
                    }
                    try:
                        requests.post(WEB_APP_URL, json=payload)
                        st.snow()
                        st.warning(f"🔴 **TIME OUT** Success for **{emp_name}** at {time_str}")
                    except:
                        st.error("May problema sa pag-sync sa Google Sheet.")
        else:
            st.error("❌ ID Number Not Found!")
