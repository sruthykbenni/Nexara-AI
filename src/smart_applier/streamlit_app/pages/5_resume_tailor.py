import sys
from pathlib import Path
import json
import streamlit as st
from io import BytesIO

# -------------------------
# Add project src to path
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src" / "smart_applier"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from smart_applier.agents.resume_tailor_agent import ResumeTailorAgent
from smart_applier.agents.resume_builder_agent import ResumeBuilderAgent
from smart_applier.utils.path_utils import get_data_dirs

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="Resume Tailor", page_icon="🎯", layout="wide")
st.title("🎯 Resume Tailor Agent")
st.write("Tailor your resume to a specific job description — personalized summary and skill emphasis!")

# -------------------------
# Directory Setup
# -------------------------
dirs = get_data_dirs()
PROFILE_DIR = dirs["profiles"]
OUTPUT_DIR = dirs["resumes"]

# -------------------------
# Choose Profile
# -------------------------
profile_files = list(PROFILE_DIR.glob("*.json"))
if not profile_files:
    st.warning("⚠️ No profiles found. Please create one first in the Profile Creator.")
    st.stop()

selected_profile = st.selectbox("Select Profile", profile_files)
user_id = selected_profile.stem
with open(selected_profile, "r", encoding="utf-8") as f:
    profile = json.load(f)

# -------------------------
# Job Description Input
# -------------------------
st.header("Job Description Input")
job_desc = st.text_area("Paste the job description here:", height=250)

# -------------------------
# Tailor Resume
# -------------------------
if st.button("✨ Tailor Resume"):
    if not job_desc.strip():
        st.warning("⚠️ Please paste a job description first.")
        st.stop()

    try:
        tailor = ResumeTailorAgent()
        tailored_profile = tailor.tailor_profile(profile, job_desc)

        # Rebuild tailored resume PDF
        builder = ResumeBuilderAgent(tailored_profile)
        pdf_buffer = builder.build_resume()

        # Save tailored resume
        output_path = OUTPUT_DIR / f"{user_id}_Tailored_Resume.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_buffer.getvalue())

        st.success(f"✅ Tailored resume generated successfully: {output_path.name}")

        st.download_button(
            "⬇️ Download Tailored Resume PDF",
            data=pdf_buffer.getvalue(),
            file_name=f"{user_id}_Tailored_Resume.pdf",
            mime="application/pdf",
        )

        with st.expander("🔍 View Tailored Profile JSON"):
            st.json(tailored_profile)

    except Exception as e:
        st.error(f"❌ Error tailoring resume: {e}")
