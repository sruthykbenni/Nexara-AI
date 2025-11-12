import sys
from pathlib import Path
import pandas as pd
import streamlit as st
import json

# -------------------------
# Add project src to path
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src" / "smart_applier"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from smart_applier.agents.profile_agent import UserProfileAgent
from smart_applier.agents.job_matching_agent import JobMatchingAgent
from smart_applier.agents.job_scraper_agent import JobScraperAgent
from smart_applier.utils.path_utils import get_data_dirs

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="Smart Job Matcher", page_icon="🔍", layout="wide")
st.title("🔍 Smart Job Matcher")
st.caption("Scrape the latest jobs from Karkidi, then match them to your profile automatically.")

# -------------------------
# Directory Setup
# -------------------------
dirs = get_data_dirs()
PROFILE_DIR = dirs["profiles"]
JOBS_DIR = dirs["jobs"]
RESULTS_FILE = JOBS_DIR / "top_matched_jobs.csv"

profile_agent = UserProfileAgent(PROFILE_DIR)
matcher = JobMatchingAgent()
scraper = JobScraperAgent(str(JOBS_DIR))

# =========================================================
# 👤 Step 1: Select Profile
# =========================================================
st.header("Step 1: Select Your Profile")

profile_files = list(PROFILE_DIR.glob("*.json"))
if not profile_files:
    st.warning("⚠️ No profiles found. Please create one in the **Profile Creator** page first.")
    st.stop()

selected_profile_file = st.selectbox("Choose your profile:", profile_files)
with open(selected_profile_file, "r", encoding="utf-8") as f:
    profile_dict = json.load(f)
user_id = selected_profile_file.stem
st.success(f"✅ Loaded profile for `{user_id}`")

st.divider()


# =========================================================
# 🕸️ Step 2: Scrape Latest Jobs (optional)
# =========================================================
st.header("Step 2: Scrape Latest Jobs from Karkidi")

pages = st.slider("Number of pages to scrape", min_value=1, max_value=10, value=3)
if st.button("🕸️ Scrape Jobs Now"):
    try:
        state = {"job_data": pd.DataFrame()}
        with st.spinner(f"Scraping {pages} pages from Karkidi..."):
            result_state = scraper.scrape_karkidi(state, pages=pages)
        df_scraped = result_state["job_data"]

        if not df_scraped.empty:
            st.success(f"✅ Scraped {len(df_scraped)} jobs successfully!")
            st.dataframe(df_scraped.head(10))
            st.info(f"Jobs saved to `{JOBS_DIR}` folder.")
        else:
            st.warning("⚠️ No jobs were scraped. The website might have changed.")
    except Exception as e:
        st.error(f"❌ Error during scraping: {e}")

st.divider()


# =========================================================
# 📄 Step 3: Select Job Dataset
# =========================================================
st.header("Step 3: Select Job Dataset (from Scraper)")

job_files = list(JOBS_DIR.glob("karkidi_jobs_*.csv"))
if not job_files:
    st.warning("⚠️ No job CSVs found. Try scraping jobs first in Step 0.")
    st.stop()

selected_job_file = st.selectbox("Choose a job file:", job_files)
st.write(f"📄 Using job dataset: `{selected_job_file.name}`")

st.divider()

# =========================================================
# 🤖 Step 4: Run Job Matching
# =========================================================
st.header("Step 4: Run Job Matching")

if st.button("🚀 Match Jobs to My Profile"):
    try:
        jobs_df = pd.read_csv(selected_job_file)
        if jobs_df.empty:
            st.warning("⚠️ Job CSV is empty. Try scraping again.")
            st.stop()

        # Normalize column names
        jobs_df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"), inplace=True)

        # Run matching process
        user_vector = matcher.embed_user_profile(profile_dict)
        job_vectors = matcher.embed_jobs(jobs_df)
        top_jobs = matcher.match_jobs(user_vector, jobs_df, job_vectors, top_k=10)

        # Ensure match_score column exists
        if "match_score" not in top_jobs.columns:
            st.warning("⚠️ 'match_score' column missing — adding placeholder values.")
            top_jobs["match_score"] = 0.0

        # Save & display
        top_jobs.to_csv(RESULTS_FILE, index=False, encoding="utf-8-sig")
        st.success(f"✅ Top matched jobs saved to `{RESULTS_FILE.name}`")
        st.dataframe(top_jobs[["title", "company", "location", "match_score"]])

        # Download button
        st.download_button(
            label="⬇️ Download Matched Jobs CSV",
            data=top_jobs.to_csv(index=False).encode("utf-8"),
            file_name="top_matched_jobs.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"❌ Error while matching jobs: {e}")
