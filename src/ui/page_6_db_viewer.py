# ui/page_6_db_viewer.py
import streamlit as st
import pandas as pd
from smart_applier.utils.db_utils import (
    get_all_profiles,
    get_all_jobs,
    get_all_resumes,
)
import json

@st.cache_data(ttl=60)
def fetch_all_data():
    """Fetch all DB content with caching to reduce reload lag."""
    return {
        "profiles": get_all_profiles(),
        "jobs": get_all_jobs(limit=200),
        "resumes": get_all_resumes(),
    }

def run():
    st.title("🗂️ Database Viewer (Admin Panel)")
    st.caption("Monitor all stored data — profiles, scraped jobs, and resumes — from the Smart Applier database.")
    st.info("⚠️ This panel is **read-only**. Editing or deleting records is not supported here for data safety.")

    # -------------------------
    # Load and cache data
    # -------------------------
    with st.spinner("Loading data from database..."):
        data = fetch_all_data()

    profiles, jobs, resumes = data["profiles"], data["jobs"], data["resumes"]

    # -------------------------
    # Summary Metrics
    # -------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("👤 Total Profiles", len(profiles))
    col2.metric("💼 Total Jobs", len(jobs))
    col3.metric("📄 Total Resumes", len(resumes))

    st.markdown("---")

    # -------------------------
    # Tabs
    # -------------------------
    tab1, tab2, tab3 = st.tabs(["👤 Profiles", "💼 Jobs", "📄 Resumes"])

    # --- Profiles ---
    with tab1:
        st.subheader("👤 User Profiles")
        if profiles:
            for p in profiles:
                with st.expander(f"📘 {p.get('name', 'Unnamed')} ({p.get('user_id')})"):
                    st.json(p, expanded=False)
        else:
            st.info("No profiles found in database.")

    # --- Jobs ---
    with tab2:
        st.subheader("💼 Job Listings (Latest 200)")
        if jobs:
            df = pd.DataFrame(jobs)
            st.dataframe(df)
            st.download_button(
                label="⬇️ Download Jobs CSV",
                data=df.to_csv(index=False),
                file_name="all_jobs.csv",
                mime="text/csv",
            )
        else:
            st.info("No job data found in database.")

    # --- Resumes ---
    with tab3:
        st.subheader("📄 Resumes Generated")
        if resumes:
            df = pd.DataFrame(resumes)
            df_display = df[["user_id", "resume_type", "file_path", "created_at"]] if "created_at" in df.columns else df
            st.dataframe(df_display)
        else:
            st.info("No resumes found in database.")
