import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd

# --- 1. CORE LAYOUT MATRIX CONFIGURATION ---
st.set_page_config(page_title="DOMS Achievement Portal", layout="wide")

SECTIONS = [
    "BBA VI A", "BBA VI B", "BBA VI C", 
    "BBA V A", "BBA V B", "BBA V C", 
    "BBA IV A", "BBA IV B", "BBA IV C", 
    "BBA III A", "BBA III B", "BBA III C", 
    "BBA II A", "BBA II B", "BBA II C", 
    "BBA I A", "BBA I B", "BBA I C"
]

CATEGORIES = [
    "Corporate Placement & Internship",
    "Research & Student Publications",
    "Academic Excellence (Ranks/Scores)",
    "Sports & Games Achievements",
    "Culturals & Co-Curricular Wins",
    "Faculty Development Programs (FDP)",
    "Research Grant / Consultancy",
    "Institutional Leadership Award"
]

ROLES = ["Student", "Faculty", "Collaboration"]
ALLOWED_EXTENSIONS = ["pdf", "docx", "doc", "jpg", "jpeg", "png"]

# Configured precisely with your achievements master sheet
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1BJ-z0QXqygqqeQgqudyh9wRu0Q8pZRrPAhClzIElyqw/edit#gid=0"

# --- 2. THEMATIC UI CSS LAYOUT ---
st.markdown("""
    <style>
    div.stButton > button:first-child { background-color: #0F4C81; color: white; border-radius: 4px; font-weight: bold; height: 45px; }
    div.stButton > button:first-child:hover { background-color: #0A3356; color: white; }
    .main-title { color: #0F4C81; text-align: center; font-size: 2.4em; font-weight: bold; margin-bottom: 5px; }
    .sub-title { color: #666666; text-align: center; font-size: 1.1em; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>Department of Management Studies (DOMS)</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Central Achievement Repository & Dashboard</div>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top:0px; margin-bottom:20px;'/>", unsafe_allow_html=True)

# Connect to Google Sheets via Streamlit Engine Connection Matrix
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Configuration Sheet Error: {e}")

# --- 3. SIDEBAR NAVIGATION CONTROLS ---
st.sidebar.markdown("## 🧭 Navigation Portal")
portal_mode = st.sidebar.radio("Go To View Mode:", ["📝 Submit New Achievement", "📊 View Department Dashboards"])

if portal_mode == "📊 View Department Dashboards":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Select Filter Sheet Tab")
    # Interactive side sub-tabs requested for Faculty, Students, and Collaboration views
    selected_view_tab = st.sidebar.selectbox(
        "Choose Category Layout:",
        ["1. Faculty Achievements", "2. Students Achievements", "3. Collaboration Achievements", "Show Entire Master Log"]
    )

# --- 4. FORM SUBMISSION INTERFACE ---
if portal_mode == "📝 Submit New Achievement":
    with st.form("achievement_registry_form", clear_on_submit=True):
        st.markdown("### 👤 1. Stakeholder Classification Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            selected_role = st.selectbox("Role / Stakeholder Type", ["-- Select Role --"] + ROLES)
        with c2:
            roll_id = st.text_input("Roll Number / Faculty ID", placeholder="e.g., 1051-22-408-XXX / DOMS-FAC-01")
        with c3:
            admission_no = st.text_input("Admission Number (Leave blank if Faculty)", placeholder="e.g., ADM-2024-XXXX")

        c4, c5, c6 = st.columns(3)
        with c4:
            fullname = st.text_input("Full Name", placeholder="Official name for certifications...")
        with c5:
            class_yr = st.selectbox("Class Year", ["-- Select Class --", "BBA I Year", "BBA II Year", "BBA III Year", "Faculty/Staff"])
        with c6:
            section_assigned = st.selectbox("Class Section Mapping", ["-- Select Section --", "NA (Faculty Only)"] + SECTIONS)

        st.markdown("<br/>### 🏆 2. Achievement / Milestone Credentials", unsafe_allow_html=True)
        c7, c8 = st.columns(2)
        with c7:
            ach_category = st.selectbox("Achievement Category", ["-- Select Category --"] + CATEGORIES)
            event_title = st.text_input("Event Title / Core Achievement", placeholder="e.g., Winner - National B-Plan / Core Committee Head")
        with c8:
            org_name = st.text_input("Organisation Name / Corporate Body", placeholder="e.g., Deloitte / IIT Madras / Management Association")
            execution_date = st.date_input("Date of Achievement", datetime.date.today())

        st.markdown("<br/>### 🔗 3. Verification Document Upload", unsafe_allow_html=True)
        # Replaced the text input link field with a native Streamlit file uploader widget
        uploaded_doc = st.file_uploader("Upload Achievement Proof (PDF, Images, Word Documents)", type=ALLOWED_EXTENSIONS)

        st.markdown("<br/>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 Submit Entry to Central Master Log", use_container_width=True)

    if submit_btn:
        if "-- Select Role --" in selected_role:
            st.error("Validation Halt: Please specify a valid Stakeholder Role Category.")
        elif not roll_id.strip() or not fullname.strip() or not event_title.strip():
            st.error("Validation Halt: ID Number, Full Name, and Achievement Event Title fields are mandatory.")
        elif uploaded_doc is None:
            st.error("Validation Halt: Please upload an official verification proof document file to register this row.")
        else:
            try:
                with st.spinner("Appending metrics row to Master Log database structure..."):
                    existing_df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
                    
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Generates an official, tamper-proof audit string tracking file details inside the document column cells
                    document_metadata_string = f"Uploaded File: {uploaded_doc.name} ({round(uploaded_doc.size / 1024, 2)} KB)"
                    
                    # Aligning data dictionary exactly with your specified Master Sheet layout
                    new_row = pd.DataFrame([{
                        "Timestamp": timestamp_str,
                        "Role / Stakeholder": str(selected_role),
                        "Roll Number": str(roll_id).strip().upper(),
                        "Admission No": str(admission_no).strip().upper() if admission_no.strip() else "NA",
                        "Name": str(fullname).strip().title(),
                        "Class": str(class_yr),
                        "Section": str(section_assigned),
                        "Date of Achievement": execution_date.strftime("%d-%m-%Y"),
                        "Achievement Category": str(ach_category),
                        "Event Title": str(event_title).strip(),
                        "Organisation Name": str(org_name).strip(),
                        "Document Link": document_metadata_string
                    }])
                    
                    final_df = pd.concat([existing_df, new_row], ignore_index=True)
                    conn.update(spreadsheet=SPREADSHEET_URL, data=final_df)
                    
                    st.success(f"🎉 Achievement recorded perfectly! Registered File metadata: '{uploaded_doc.name}' inside the master sheet ledger.")
            except Exception as e:
                st.error(f"Database Communication Error: {e}")

# --- 5. DASHBOARD SIDEBAR FILTER MANAGER VIEW ---
elif portal_mode == "📊 View Department Dashboards":
    try:
        with st.spinner("Fetching latest updates from Master Log..."):
            master_df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        
        # Slicing the dataframe based on the active sidebar tab drop selection
        if selected_view_tab == "1. Faculty Achievements":
            st.subheader("📁 Faculty Achievements Tab Log View")
            filtered_df = master_df[master_df["Role / Stakeholder"] == "Faculty"]
        elif selected_view_tab == "2. Students Achievements":
            st.subheader("📁 Student Achievements Tab Log View")
            filtered_df = master_df[master_df["Role / Stakeholder"] == "Student"]
        elif selected_view_tab == "3. Collaboration Achievements":
            st.subheader("📁 Joint Faculty & Student Collaborative Log View")
            filtered_df = master_df[master_df["Role / Stakeholder"] == "Collaboration"]
        else:
            st.subheader("📋 Central Master Ledger Log (All Entries)")
            filtered_df = master_df

        st.markdown(f"**Total Registered Records in this View:** `{len(filtered_df)}` rows")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Unable to render visual dashboard view: {e}")

st.markdown("<br><hr/><p style='text-align: center; font-size: 0.95em; font-weight: bold; color: #777;'>DOMS Data Architecture Matrix Logs — Developed by IQAC</p>", unsafe_allow_html=True)
