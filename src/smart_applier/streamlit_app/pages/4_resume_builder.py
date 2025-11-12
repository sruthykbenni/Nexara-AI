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

from smart_applier.agents.resume_builder_agent import ResumeBuilderAgent
from smart_applier.utils.path_utils import get_data_dirs

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="Resume Builder", page_icon="📄", layout="wide")
st.title("📄 Resume Builder")
st.write("Generate an ATS-friendly resume PDF directly from your saved profile.")

# -------------------------
# Directory Setup
# -------------------------
dirs = get_data_dirs()
PROFILE_DIR = dirs["profiles"]
OUTPUT_DIR = dirs["resumes"]

# -------------------------
# Select Profile
# -------------------------
profile_files = list(PROFILE_DIR.glob("*.json"))
if not profile_files:
    st.warning("⚠️ No profiles found. Please create one in the **Profile Creator** first.")
    st.stop()

selected_profile = st.selectbox("Select Profile", profile_files)
with open(selected_profile, "r", encoding="utf-8") as f:
    profile = json.load(f)
user_id = selected_profile.stem

# -------------------------
# Build Resume
# -------------------------
if st.button("🚀 Build Resume"):
    try:
        builder = ResumeBuilderAgent(profile)
        pdf_buffer = builder.build_resume()

        # Save to disk
        output_path = OUTPUT_DIR / f"{user_id}_Resume.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_buffer.getvalue())

        st.success(f"✅ Resume generated successfully: {output_path.name}")

        st.download_button(
            "⬇️ Download Resume PDF",
            data=pdf_buffer.getvalue(),
            file_name=f"{user_id}_Resume.pdf",
            mime="application/pdf",
        )

    except Exception as e:
        st.error(f"❌ Error generating resume: {e}")
