import streamlit as st
import os
from pathlib import Path

# 🧩 Database setup
from smart_applier.database.db_setup import initialize_database, load_sample_data
from smart_applier.utils.path_utils import get_data_dirs

# ✅ Ensure database exists on first run (Cloud-safe)
paths = get_data_dirs()
db_path = paths["root"] / "smart_applier.db"
if not db_path.exists():
    os.makedirs(paths["root"], exist_ok=True)
    print("🧩 Creating database...")
    initialize_database()
    load_sample_data()  # optional demo data for first-time users

# 🧩 Import all UI page modules
from ui import (
    page_1_create_profile,
    page_2_resume_builder,
    page_3_external_jd,
    page_4_job_scraper,
    page_5_skill_gap_analyzer,
    page_6_db_viewer,
)

# -------------------------
# 🧠 Streamlit Configuration
# -------------------------
st.set_page_config(
    page_title="Smart Applier AI",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# 🌱 Initialize Session State
# -------------------------
if "profile_data" not in st.session_state:
    st.session_state["profile_data"] = None
if "job_data" not in st.session_state:
    st.session_state["job_data"] = None
if "matched_jobs" not in st.session_state:
    st.session_state["matched_jobs"] = None

# -------------------------
# 🧠 App Header
# -------------------------
st.markdown(
    """
    <div style="text-align:center; margin-bottom: 10px;">
        <h1 style="color:#003366;">🧠 Smart Applier AI</h1>
        <p style="font-size:17px;">Your Intelligent Career Assistant — build, match, tailor, and upskill with AI.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# 📂 Sidebar Navigation
# -------------------------
st.sidebar.header("🔍 Navigation")
page = st.sidebar.radio(
    "Choose a section:",
    [
        "Create Profile",
        "Resume Builder",
        "External JD Flow",
        "Job Scraper Flow",
        "Skill Gap Analyzer",
        "Database Viewer (Admin)",
    ],
    index=0
)

# -------------------------
# 🚀 Page Routing
# -------------------------
if page == "Create Profile":
    page_1_create_profile.run()

elif page == "Resume Builder":
    page_2_resume_builder.run()

elif page == "External JD Flow":
    page_3_external_jd.run()

elif page == "Job Scraper Flow":
    page_4_job_scraper.run()

elif page == "Skill Gap Analyzer":
    page_5_skill_gap_analyzer.run()

elif page == "Database Viewer (Admin)":
    page_6_db_viewer.run()
