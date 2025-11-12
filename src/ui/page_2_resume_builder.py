# ui/page_2_resume_builder.py
import streamlit as st
import io
from smart_applier.agents.resume_builder_agent import ResumeBuilderAgent
from smart_applier.agents.profile_agent import UserProfileAgent

def run():
    st.title("📄 Resume Builder")
    st.caption("Generate an ATS-friendly resume PDF from your saved profile.")

    # -------------------------
    # Load Profile Options
    # -------------------------
    profile_agent = UserProfileAgent()
    profiles_meta = profile_agent.list_profiles()

    if not profiles_meta:
        st.warning("⚠️ No profiles found. Please create one on the 'Create Profile' page first.")
        return

    profile_labels = [f"{p.get('name', 'Unknown')} ({p.get('user_id')})" for p in profiles_meta]
    selected_label = st.selectbox("Select a saved profile", profile_labels)
    selected_user_id = profiles_meta[profile_labels.index(selected_label)]["user_id"]

    # -------------------------
    # Generate Resume
    # -------------------------
    if st.button("💼 Build Resume"):
        try:
            with st.spinner("Building your professional resume..."):
                profile = profile_agent.load_profile(selected_user_id)
                if not profile:
                    st.error("⚠️ Could not load profile from database.")
                    return

                builder = ResumeBuilderAgent(profile)
                buffer = builder.build_resume()  # returns BytesIO
                pdf_bytes = buffer.getvalue()

                st.success("✅ Resume generated successfully!")
                st.download_button(
                    label="⬇️ Download Resume PDF",
                    data=pdf_bytes,
                    file_name=f"{selected_user_id}_Resume.pdf",
                    mime="application/pdf",
                )

                # Optionally, show preview if small file
                if len(pdf_bytes) < 2_000_000:  # <2MB
                    st.pdf(buffer)

        except Exception as e:
            st.error(f"❌ Error generating resume: {e}")
