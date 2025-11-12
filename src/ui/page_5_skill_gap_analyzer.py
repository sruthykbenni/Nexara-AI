# ui/page_5_skill_gap_analyzer.py
import streamlit as st
from smart_applier.agents.skill_gap_agent import SkillGapAgent
from smart_applier.agents.resume_tailor_agent import ResumeTailorAgent
from smart_applier.agents.profile_agent import UserProfileAgent
import os
import traceback

@st.cache_resource
def get_profile_agent():
    return UserProfileAgent()

def run():
    st.title("📊 Skill Gap Analyzer")
    st.caption("Identify missing skills and get AI-powered learning recommendations — tailored to your profile or a specific job description.")

    # -------------------------
    # Load Profiles
    # -------------------------
    profile_agent = get_profile_agent()
    profiles_meta = profile_agent.list_profiles()
    if not profiles_meta:
        st.warning("⚠️ No profiles found. Please create one first.")
        return

    profile_labels = [f"{p.get('name', 'Unknown')} ({p.get('user_id')})" for p in profiles_meta]
    selected_label = st.selectbox("Select Profile", profile_labels)
    selected_user_id = profiles_meta[profile_labels.index(selected_label)]["user_id"]

    # -------------------------
    # Analyze Top Matched Jobs
    # -------------------------
    st.markdown("---")
    st.subheader("📈 Analyze Against Top Matched Jobs")

    if st.button("🔍 Analyze My Matched Jobs"):
        try:
            with st.spinner("Analyzing skill gaps from your latest matched jobs..."):
                agent = SkillGapAgent(user_id=selected_user_id)
                recs = agent.get_recommendations()

                if not recs:
                    st.success("🎯 No missing skills detected — your profile aligns very well!")
                else:
                    st.subheader("🚀 Missing Skills & Learning Recommendations")
                    for skill, resources in recs.items():
                        st.markdown(f"**🧠 {skill.title()}**")
                        for r in resources:
                            st.write(f"- {r}")
            st.toast("✅ Skill gap analysis complete!", icon="✅")

        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.text(traceback.format_exc())

    # -------------------------
    # Analyze Custom JD
    # -------------------------
    st.markdown("---")
    st.subheader("🧩 Analyze Custom Role or Job Description")

    jd_text = st.text_area("Paste job description here", height=250, placeholder="Paste a JD from LinkedIn, Karkidi, etc.")

    if jd_text.strip() and st.button("🧠 Analyze Custom JD"):
        try:
            if not os.getenv("GEMINI_API_KEY"):
                st.warning("⚠️ Gemini API key not found — using fallback text analysis.")
            
            profile = profile_agent.load_profile(selected_user_id)
            tailorer = ResumeTailorAgent()

            st.info("Step 1️⃣ Extracting key skills from job description...")
            cleaned = tailorer.clean_job_description(jd_text)
            jd_keywords = [k.strip() for k in str(cleaned).split(",") if k.strip()]
            if not jd_keywords:
                jd_keywords = [w.strip() for w in jd_text.split() if len(w) > 3]
                st.warning("⚠️ No structured keywords found — fallback extraction applied.")
            else:
                st.caption(f"🧩 Extracted JD Skills: {', '.join(jd_keywords[:15])} ...")

            st.info("Step 2️⃣ Comparing JD skills with your profile...")
            user_skills = [s.lower() for sub in profile.get("skills", {}).values() for s in sub]
            matched = tailorer.compare_skills(jd_keywords, user_skills)
            coverage = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0
            st.success(f"🎯 Skill Coverage: {coverage:.1f}% ({len(matched)} matched out of {len(jd_keywords)})")

            missing_skills = [k for k in jd_keywords if k.lower() not in matched]
            if missing_skills:
                st.warning(f"🚧 Missing Skills: {', '.join(missing_skills[:10])} ...")
                st.subheader("📚 Learning Resources")
                skill_agent = SkillGapAgent(selected_user_id)
                for skill in missing_skills:
                    resources = skill_agent.get_learning_resources(skill)
                    if resources:
                        st.markdown(f"**{skill.title()}**")
                        for r in resources:
                            st.write(f"- {r}")
                    else:
                        st.write(f"- No resources found for {skill}.")
            else:
                st.success("✅ No missing skills for this JD!")

            st.toast("📈 Custom JD Analysis Complete!", icon="✅")

        except Exception as e:
            st.error(f"❌ Custom JD Analysis Failed: {e}")
            st.text(traceback.format_exc())
