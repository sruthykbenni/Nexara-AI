# ui/page_1_create_profile.py
import streamlit as st
import json
from io import BytesIO
from smart_applier.agents.profile_agent import UserProfileAgent

def run():
    st.title("🧠 Create Your Smart Applier Profile")
    st.caption("Build your professional data once — use it for resumes, job matching, and tailoring.")

    profile_agent = UserProfileAgent()

    # -------------------------
    # Personal Details
    # -------------------------
    st.header("👤 Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
    with col2:
        location = st.text_input("Location (City, State)")
        github = st.text_input("GitHub URL")
        linkedin = st.text_input("LinkedIn URL")

    # -------------------------
    # Resume Upload (optional)
    # -------------------------
    st.header("📄 Resume Upload (Optional)")
    uploaded_resume = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    resume_bytes = None
    resume_filename = None
    if uploaded_resume:
        resume_bytes = uploaded_resume.getvalue()
        resume_filename = uploaded_resume.name
        st.success(f"✅ {resume_filename} uploaded successfully!")

    # -------------------------
    # Education
    # -------------------------
    st.header("🎓 Education")
    education = st.text_area(
        "List your education (one per line):",
        placeholder="M.Sc. Computer Science, Digital University Kerala (2026)"
    )

    # -------------------------
    # Skills
    # -------------------------
    st.header("💡 Skills")
    st.info("Organize your skills by category — e.g., Programming, Tools, ML, Soft Skills.")
    num_categories = st.number_input("Number of skill categories", min_value=1, max_value=10, value=3, step=1)

    skills_dict = {}
    for i in range(int(num_categories)):
        st.subheader(f"Category {i+1}")
        category = st.text_input(f"Category Name", key=f"cat_{i}")
        skills = st.text_input(f"Skills (comma-separated)", key=f"skills_{i}")
        if category:
            skills_dict[category] = [s.strip() for s in skills.split(",") if s.strip()]

    # -------------------------
    # Projects
    # -------------------------
    st.header("🚀 Projects")
    num_projects = st.number_input("Number of projects", min_value=1, max_value=10, value=1, step=1)
    projects_list = []
    for i in range(int(num_projects)):
        st.subheader(f"Project {i+1}")
        title = st.text_input(f"Title", key=f"proj_title_{i}")
        proj_skills = st.text_input(f"Skills (comma-separated)", key=f"proj_skills_{i}")
        desc = st.text_area(f"Description", key=f"proj_desc_{i}")
        if title:
            projects_list.append({
                "title": title,
                "skills": [s.strip() for s in proj_skills.split(",") if s.strip()],
                "description": desc
            })

    # -------------------------
    # Experience
    # -------------------------
    st.header("💼 Experience")
    experience = st.text_area("Describe your relevant experience (one per line)")

    # -------------------------
    # Certificates & Achievements
    # -------------------------
    st.header("🏅 Certificates & Achievements")
    num_certificates = st.number_input("Number of certificates", min_value=0, max_value=10, value=0, step=1)
    certificates_list = []
    for i in range(int(num_certificates)):
        st.subheader(f"Certificate {i+1}")
        cert_name = st.text_input(f"Certificate Name", key=f"cert_name_{i}")
        cert_source = st.text_input(f"Issued By", key=f"cert_source_{i}")
        if cert_name:
            certificates_list.append({
                "name": cert_name,
                "source": cert_source
            })

    achievements = st.text_area("Achievements (one per line)")

    # -------------------------
    # Save Button
    # -------------------------
    if st.button("💾 Save Profile"):
        if not email:
            st.error("⚠️ Please enter your email before saving.")
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
                    "resume_name": resume_filename,
                },
                "education": [e.strip() for e in education.splitlines() if e.strip()],
                "skills": skills_dict,
                "projects": projects_list,
                "experience": [e.strip() for e in experience.splitlines() if e.strip()],
                "certificates": certificates_list,
                "achievements": [a.strip() for a in achievements.splitlines() if a.strip()],
            }

            try:
                profile_agent.save_profile(profile_data, user_id)
                st.session_state["profile_data"] = profile_data  # 🧠 store in session
                st.success(f"✅ Profile saved successfully for `{user_id}`")

                with st.expander("🔍 View Profile JSON"):
                    st.json(profile_data)

                if resume_bytes:
                    st.download_button(
                        label="⬇️ Download Uploaded Resume",
                        data=resume_bytes,
                        file_name=resume_filename,
                    )

            except Exception as e:
                st.error(f"❌ Failed to save profile: {e}")
