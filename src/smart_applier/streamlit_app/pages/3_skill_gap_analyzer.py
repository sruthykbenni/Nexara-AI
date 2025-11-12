import sys
from pathlib import Path
import json
import streamlit as st

# -------------------------
# Add project src to path
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src" / "smart_applier"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from smart_applier.agents.skill_gap_agent import SkillGapAgent
from smart_applier.agents.profile_agent import UserProfileAgent
from smart_applier.utils.path_utils import get_data_dirs

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="Skill Gap Analyzer", page_icon="🧠", layout="wide")
st.title("🧠 Skill Gap Analyzer")
st.write("Identify missing skills from your top-matched jobs and get curated learning resources!")

# -------------------------
# Directory Setup
# -------------------------
dirs = get_data_dirs()
PROFILE_DIR = dirs["profiles"]
JOBS_DIR = dirs["jobs"]

# -------------------------
# Step 1: Select Profile
# -------------------------
st.header("Step 1: Select Profile")
profile_files = list(PROFILE_DIR.glob("*.json"))
if not profile_files:
    st.warning("⚠️ No profiles found. Please create one in the **Profile Creator** page first.")
    st.stop()

selected_profile_file = st.selectbox("Choose your profile:", profile_files)
user_id = selected_profile_file.stem
with open(selected_profile_file, "r", encoding="utf-8") as f:
    profile = json.load(f)
st.success(f"✅ Loaded profile for {user_id}")

# -------------------------
# Step 2: Load Matched Jobs
# -------------------------
st.header("Step 2: Select Job Match File")
job_match_files = list(JOBS_DIR.glob("top_matched_jobs.csv"))
if not job_match_files:
    st.warning("⚠️ No matched jobs found. Please run the **Job Matcher** first.")
    st.stop()

selected_jobs_file = st.selectbox("Choose matched jobs file:", job_match_files)
st.info(f"📄 Using: `{selected_jobs_file.name}`")

# -------------------------
# Step 3: Run Skill Gap Analysis
# -------------------------
if st.button("🚀 Analyze Skill Gaps"):
    try:
        agent = SkillGapAgent(user_id=user_id, jobs_file=selected_jobs_file)
        recommendations = agent.get_recommendations()

        if not recommendations:
            st.success("✅ Great job! Your profile already matches the key job requirements.")
        else:
            st.header("📚 Recommended Learning Resources")

            for skill, resources in recommendations.items():
                st.subheader(f"🎯 {skill.title()}")
                for res in resources:
                    st.markdown(f"- {res}")

            # Option to download recommendations as JSON
            st.download_button(
                label="⬇️ Download Skill Gap Report (JSON)",
                data=json.dumps(recommendations, indent=4).encode("utf-8"),
                file_name=f"{user_id}_skill_gap_report.json",
                mime="application/json",
            )

    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
