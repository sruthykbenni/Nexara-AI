# ui/page_3_external_jd.py
import streamlit as st
import io
from smart_applier.agents.resume_tailor_agent import ResumeTailorAgent
from smart_applier.agents.resume_builder_agent import ResumeBuilderAgent
from smart_applier.agents.profile_agent import UserProfileAgent
import os

def run():
    st.title("🧩 External JD Tailoring")
    st.caption("Paste a job description — Smart Applier will analyze and tailor your resume using Gemini & Semantic AI.")

    # -------------------------
    # Step 1: Load Profiles
    # -------------------------
    profile_agent = UserProfileAgent()
    profiles_meta = profile_agent.list_profiles()

    if not profiles_meta:
        st.warning("⚠️ No profiles found. Please create one on the 'Create Profile' page first.")
        return

    profile_labels = [f"{p.get('name', 'Unknown')} ({p.get('user_id')})" for p in profiles_meta]
    selected_label = st.selectbox("Select Profile", profile_labels)
    selected_user_id = profiles_meta[profile_labels.index(selected_label)]["user_id"]

    # -------------------------
    # Step 2: Paste Job Description
    # -------------------------
    jd_text = st.text_area("Paste Job Description Here", height=250, placeholder="Copy a job description from LinkedIn, Karkidi, etc.")
    if not jd_text.strip():
        st.info("💡 Paste a job description to begin tailoring.")
        return

    # -------------------------
    # Step 3: Tailor Resume
    # -------------------------
    if st.button("✨ Tailor Resume"):
        with st.spinner("Analyzing and tailoring your resume..."):
            try:
                profile = profile_agent.load_profile(selected_user_id)
                if not profile:
                    st.error("❌ Could not load profile from database.")
                    return

                # Ensure API key is available
                if not os.getenv("GEMINI_API_KEY"):
                    st.error("⚠️ Missing Gemini API Key! Please set GEMINI_API_KEY in your environment or Streamlit secrets.")
                    return

                tailorer = ResumeTailorAgent()

                # 🧠 Step 1: Extract JD keywords using Gemini
                cleaned = tailorer.clean_job_description(jd_text)
                jd_keywords = [k.strip() for k in str(cleaned).split(",") if k.strip()]

                if not jd_keywords:
                    jd_keywords = [w for w in jd_text.split() if len(w) > 3]
                    st.warning("⚠️ Gemini returned no structured skills — using fallback keyword extraction.")

                st.caption(f"🧩 Extracted Keywords: {', '.join(jd_keywords[:15])}...")

                # 🧮 Step 2: Compare skills
                user_skills = [s.lower() for sub in profile.get("skills", {}).values() for s in sub]
                matched_skills = tailorer.compare_skills(jd_keywords, user_skills)
                coverage = (len(matched_skills) / len(jd_keywords)) * 100 if jd_keywords else 0
                st.text(f"🎯 Match Coverage: {coverage:.1f}% ({len(matched_skills)} matched / {len(jd_keywords)})")

                # 💫 Step 3: Refine with Gemini
                refined_profile = tailorer.refine_with_gemini(profile, jd_keywords, matched_skills, coverage)
                if not isinstance(refined_profile, dict):
                    refined_profile = profile
                    st.warning("⚠️ Gemini returned invalid data — using base profile.")

                # 📄 Step 4: Build Tailored Resume
                builder = ResumeBuilderAgent(refined_profile)
                buffer = builder.build_resume()
                pdf_bytes = buffer.getvalue()

                st.success("✅ Tailored Resume Generated Successfully!")
                st.download_button(
                    label="⬇️ Download Tailored Resume PDF",
                    data=pdf_bytes,
                    file_name=f"{selected_user_id}_Tailored_Resume.pdf",
                    mime="application/pdf",
                )

                # Optional Preview
                if len(pdf_bytes) < 2_000_000:
                    st.pdf(buffer)

                # Cache result in session
                st.session_state["tailored_profile"] = refined_profile
                st.session_state["tailored_resume"] = pdf_bytes

            except Exception as e:
                st.error(f"❌ Tailoring failed: {e}")
