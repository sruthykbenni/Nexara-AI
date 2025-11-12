# smart_applier/agents/resume_tailor_agent.py
import os
import re
import json
import pandas as pd
import sqlite3
from io import BytesIO
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import google.generativeai as genai
from smart_applier.utils.path_utils import get_data_dirs, ensure_database_exists
from smart_applier.agents.resume_builder_agent import ResumeBuilderAgent


class ResumeTailorAgent:
    """
    Hybrid Tailoring Approach (Session-Based):
    1️⃣ Gemini extracts job-related keywords
    2️⃣ SentenceTransformer performs semantic comparison
    3️⃣ Gemini refines resume holistically (skills + summary)
    4️⃣ ResumeBuilderAgent generates tailored PDF in-memory
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ No GEMINI_API_KEY found — fallback mode (no AI refinement).")
            self.gemini_model = None
        else:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")

        self.model = SentenceTransformer(model_name)
        paths = get_data_dirs()
        self.use_in_memory = paths["use_in_memory_db"]
        self.db_path = paths["db_path"]

        if not self.use_in_memory:
            ensure_database_exists()

    # -------------------------
    # 🧠 Step 1 — Clean Job Description
    # -------------------------
    def clean_job_description(self, job_description: str):
        """Use Gemini to extract key skills and qualifications."""
        if not self.gemini_model:
            return job_description
        prompt = f"""
        Extract only the relevant 'skills', 'qualifications', and 'technical requirements'
        from this job description. Return them as a comma-separated list.
        ---
        {job_description}
        """
        try:
            response = self.gemini_model.generate_content(prompt)
            cleaned_text = response.text.strip()
            return cleaned_text
        except Exception as e:
            print(f"⚠️ Gemini JD cleaning failed: {e}")
            return job_description

    # -------------------------
    # 🧩 Step 2 — Semantic Matching
    # -------------------------
    def compare_skills(self, jd_keywords, user_skills, threshold=0.45):
        """Compute semantic overlaps between JD and user skills."""
        if not jd_keywords or not user_skills:
            return []

        jd_vecs = self.model.encode(jd_keywords, convert_to_tensor=True)
        user_vecs = self.model.encode(user_skills, convert_to_tensor=True)
        cosine = util.cos_sim(jd_vecs, user_vecs)

        matched = set()
        for i, jd_skill in enumerate(jd_keywords):
            if cosine[i].max().item() >= threshold:
                matched.add(jd_skill)
        return list(matched)

    # -------------------------
    # 💫 Step 3 — Gemini Resume Refinement
    # -------------------------
    def refine_with_gemini(self, profile, jd_keywords, matched_skills, coverage_score):
        """Refine the profile using Gemini to align with JD."""
        if not self.gemini_model:
            return profile

        prompt = f"""
        You are a resume optimizer. Rewrite the following profile to align it with the given job.
        Include:
        - Emphasize matched skills.
        - Reorder relevant projects.
        - Write a concise 3-line professional summary for a data science role.
        - Keep JSON valid and structured.
        USER PROFILE: {json.dumps(profile, indent=2)}
        JOB KEYWORDS: {', '.join(jd_keywords)}
        MATCHED SKILLS: {', '.join(matched_skills)}
        COVERAGE SCORE: {coverage_score:.2f}%
        Return JSON only, no extra text.
        """
        try:
            response = self.gemini_model.generate_content(prompt)
            text = response.text.strip()
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return profile
        except Exception as e:
            print(f"⚠️ Gemini refinement failed: {e}")
            return profile

    # -------------------------
    # 🧩 Step 4 — Tailor Profile (Full Flow)
    # -------------------------
    def tailor_profile(self, profile: dict, job_description: str) -> BytesIO:
        """
        Takes a user profile and a single job description string,
        and returns a tailored resume PDF (in-memory buffer).
        """
        # 🧹 Clean JD
        cleaned_jd = self.clean_job_description(job_description)
        jd_keywords = [kw.strip() for kw in str(cleaned_jd).split(",") if kw.strip()]

        # Extract user skills
        user_skills = [s.lower() for sub in profile.get("skills", {}).values() for s in sub]

        # Semantic comparison
        matched_skills = self.compare_skills(jd_keywords, user_skills)
        coverage_score = (len(matched_skills) / len(jd_keywords) * 100) if jd_keywords else 0
        print(f"🎯 Matched {len(matched_skills)} skills ({coverage_score:.2f}% coverage)")

        # AI refinement (optional)
        tailored_profile = self.refine_with_gemini(profile, jd_keywords, matched_skills, coverage_score)

        # 🧠 Normalize experience & projects
        for key in ["experience", "projects"]:
            items = tailored_profile.get(key, [])
            if isinstance(items, str):
                tailored_profile[key] = [{"description": items}]
            elif isinstance(items, list):
                for i, item in enumerate(items):
                    if isinstance(item, dict) and isinstance(item.get("description"), list):
                        item["description"] = " ".join(item["description"])

        # 🧾 Generate resume PDF
        builder = ResumeBuilderAgent(tailored_profile)
        pdf_buffer = builder.build_resume()

        # Optional metadata save
        self._save_to_db(profile, coverage_score)
        return pdf_buffer

    # -------------------------
    # 💾 Optional: Log tailoring metadata
    # -------------------------
    def _save_to_db(self, profile, coverage_score):
        """Save summary metadata to DB (optional, not persistent)."""
        try:
            conn = sqlite3.connect(":memory:" if self.use_in_memory else self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tailored_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT,
                    coverage_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            email = profile.get("personal", {}).get("email", "unknown")
            cursor.execute(
                "INSERT INTO tailored_sessions (user_email, coverage_score) VALUES (?, ?)",
                (email, coverage_score),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Could not log tailoring metadata: {e}")
