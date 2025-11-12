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

from smart_applier.agents.profile_agent import UserProfileAgent
from smart_applier.utils.path_utils import get_data_dirs

# -------------------------
# Directory Setup
# -------------------------
dirs = get_data_dirs()
DATA_DIR = dirs["profiles"]
RESUME_DIR = dirs["resumes"]

profile_agent = UserProfileAgent(DATA_DIR)

# -------------------------
# Streamlit Page Config
# -------------------------
st.set_page_config(page_title="Smart Applier - Profile Creator", layout="wide")
st.title("🧠 Smart Applier - Create Your Profile")
st.subheader("Fill in your details below to save your professional profile.")

# -------- Personal Details --------
st.header("Personal Details")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
with col2:
    location = st.text_input("Location")
    github = st.text_input("GitHub URL")
    linkedin = st.text_input("LinkedIn URL")

# -------- Resume Upload --------
st.header("Resume Upload")
resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
resume_path = None
if resume_file and email:
    resume_filename = f"{email.split('@')[0]}_{resume_file.name}"
    resume_path = RESUME_DIR / resume_filename
    with open(resume_path, "wb") as f:
        f.write(resume_file.getbuffer())
    st.success(f"📄 Resume saved as: {resume_filename}")

# -------- Education --------
st.header("Education")
education = st.text_area(
    "List your education (one per line, e.g., M.Sc. Computer Science with Specialization in Data Analytics, 2026)"
)

# -------- Skills --------
st.header("Skills")
st.info("Enter skills by category. Example:\nProgramming & Tools: Python, SQL, Power BI")
num_categories = st.number_input("Number of skill categories", min_value=1, max_value=10, value=3, step=1)

skills_dict = {}
for i in range(int(num_categories)):
    st.subheader(f"Category {i+1}")
    category = st.text_input(f"Category {i+1} Name (e.g., Programming & Tools)", key=f"cat_name_{i}")
    skills_line = st.text_input(f"Skills for Category {i+1} (comma-separated)", key=f"cat_skills_{i}")
    if category:
        skills_dict[category] = [s.strip() for s in skills_line.split(",") if s.strip()]

# -------- Projects --------
st.header("Projects")
num_projects = st.number_input("Number of projects", min_value=1, max_value=10, value=1, step=1)
projects_list = []
for i in range(int(num_projects)):
    st.subheader(f"Project {i+1}")
    title = st.text_input(f"Project {i+1} Title", key=f"proj_title_{i}")
    proj_skills = st.text_input(f"Project {i+1} Skills (comma-separated)", key=f"proj_skills_{i}")
    description = st.text_area(f"Project {i+1} Description", key=f"proj_desc_{i}")
    projects_list.append({
        "title": title,
        "skills": [s.strip() for s in proj_skills.split(",") if s.strip()],
        "description": description
    })

# -------- Experience --------
st.header("Experience")
experience = st.text_area("List your experiences (one per line)")

# -------- Certificates & Achievements --------
st.header("Certificates & Achievements")
num_certificates = st.number_input("Number of certificates", min_value=0, max_value=10, value=0, step=1)
certificates_list = []
for i in range(int(num_certificates)):
    st.subheader(f"Certificate {i+1}")
    cert_name = st.text_input(f"Certificate {i+1} Name", key=f"cert_name_{i}")
    cert_source = st.text_input(f"Certificate {i+1} Source", key=f"cert_source_{i}")
    certificates_list.append({
        "name": cert_name,
        "source": cert_source
    })

achievements = st.text_area("Achievements (one per line)")

# -------- Submit Button --------
if st.button("💾 Save Profile"):
    if not email:
        st.error("⚠️ Please enter your email to save the profile.")
    else:
        user_id = email.split("@")[0]
        profile_data = {
            "personal": {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "github": github,
                "linkedin": linkedin,
                "resume_path": str(resume_path) if resume_path else None,
            },
            "education": [e.strip() for e in education.splitlines() if e.strip()],
            "skills": skills_dict,
            "projects": [p for p in projects_list if p["title"]],
            "experience": [e.strip() for e in experience.splitlines() if e.strip()],
            "certificates": [c for c in certificates_list if c["name"]],
            "achievements": [a.strip() for a in achievements.splitlines() if a.strip()],
        }

        try:
            path = profile_agent.save_profile(profile_data, user_id)
            st.success(f"✅ Profile saved successfully at: `{path}`")

            with st.expander("🔍 View Saved JSON"):
                st.json(profile_data)

        except Exception as e:
            st.error(f"❌ Failed to save profile: {e}")
