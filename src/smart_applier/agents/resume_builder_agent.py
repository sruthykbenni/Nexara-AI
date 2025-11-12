# smart_applier/agents/resume_builder_agent.py
import io
import json
import os
import re
import sqlite3
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors
from dotenv import load_dotenv
from smart_applier.utils.path_utils import get_data_dirs, ensure_database_exists


class ResumeBuilderAgent:
    """
    Generates an ATS-friendly resume PDF in-memory (session-based).
    Gemini is used only if API key is provided.
    """

    def __init__(self, user_profile: dict, user_id: str = "session_user"):
        # Parse or validate profile
        if isinstance(user_profile, str):
            try:
                user_profile = json.loads(user_profile)
            except json.JSONDecodeError:
                raise ValueError("❌ Invalid profile JSON.")
        self.profile = user_profile
        self.user_id = user_id
        self.buffer = io.BytesIO()

        # Setup paths & DB mode
        paths = get_data_dirs()
        self.use_in_memory = paths["use_in_memory_db"]
        self.db_path = paths["db_path"]

        if not self.use_in_memory:
            ensure_database_exists()

        # Gemini setup
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("models/gemini-2.5-flash")
            except Exception as e:
                print(f"⚠️ Gemini init failed: {e}")
        else:
            print("⚠️ No GEMINI_API_KEY found — using fallback summary.")

    # -------------------------
    # 🧠 Generate Gemini summary
    # -------------------------
    def generate_clean_summary(self):
        if not self.model:
            return None
        try:
            skills = self.profile.get("skills", {})
            projects = self.profile.get("projects", [])
            experience = self.profile.get("experience", [])

            prompt = (
                "You are a professional resume writer.\n"
                "Write a concise 3-line professional summary for this candidate.\n"
                "Focus on data-driven skills, achievements, and professional tone.\n"
                "Avoid pronouns like I/my/we.\n\n"
                f"Skills: {skills}\nProjects: {projects}\nExperience: {experience}\n"
            )
            response = self.model.generate_content(prompt)
            summary = re.sub(r"[*•\-]+", "", response.text.strip())
            summary = re.sub(r"\n+", " ", summary)
            summary = re.sub(r"\b(I|my|me|our|we|us)\b", "", summary, flags=re.I)
            return summary.strip()
        except Exception as e:
            print(f"⚠️ Gemini summary generation failed: {e}")
            return None

    # -------------------------
    # 📄 Build Resume
    # -------------------------
    def build_resume(self):
        """Creates a PDF resume in-memory and returns a BytesIO buffer."""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            leftMargin=50,
            rightMargin=50,
            topMargin=50,
            bottomMargin=30,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title", fontSize=20, textColor=colors.HexColor("#003366"),
            alignment=TA_CENTER, spaceAfter=12, leading=22
        )
        header_style = ParagraphStyle(
            "Header", fontSize=14, textColor=colors.HexColor("#003366"),
            spaceAfter=4, leading=18
        )
        normal_style = ParagraphStyle("Normal", fontSize=10, leading=14)
        bullet_style = ParagraphStyle("Bullet", leftIndent=15, fontSize=10, leading=12)

        elements = []

        # --- Header ---
        personal = self.profile.get("personal", {})
        name = personal.get("name", "Your Name")
        email = personal.get("email", "")
        phone = personal.get("phone", "")
        location = personal.get("location", "")
        linkedin = personal.get("linkedin", "")
        github = personal.get("github", "")

        elements.append(Paragraph(f"<b>{name}</b>", title_style))
        elements.append(Spacer(1, 6))
        contact_info = f"{email} | {phone} | {location}"
        elements.append(Paragraph(contact_info, ParagraphStyle("center", alignment=TA_CENTER, fontSize=10)))
        if linkedin or github:
            links = " | ".join(filter(None, [linkedin, github]))
            elements.append(Paragraph(links, ParagraphStyle("links", alignment=TA_CENTER, fontSize=10, textColor=colors.blue)))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", color=colors.HexColor("#003366"), thickness=0.6))
        elements.append(Spacer(1, 10))

        # --- Summary ---
        summary = self.profile.get("summary") or self.generate_clean_summary()
        if not summary:
            summary = (
                "Results-driven data analyst skilled in Python, Power BI, and cloud analytics. "
                "Adept at transforming data into actionable insights."
            )
        self.generated_summary = summary
        elements.append(Paragraph("Professional Summary", header_style))
        elements.append(Paragraph(summary, normal_style))
        elements.append(Spacer(1, 12))

        # --- Skills ---
        skills = self.profile.get("skills", {})
        if skills:
            elements.append(Paragraph("Skills", header_style))
            for category, skill_list in skills.items():
                skill_text = ", ".join(skill_list)
                elements.append(Paragraph(f"<b>{category}:</b> {skill_text}", normal_style))
            elements.append(Spacer(1, 8))

        # --- Education ---
        education = self.profile.get("education", [])
        if education:
            elements.append(Paragraph("Education", header_style))
            for edu in education:
                text = edu if isinstance(edu, str) else f"{edu.get('degree', '')} — {edu.get('institution', '')}"
                elements.append(Paragraph(text, normal_style))
            elements.append(Spacer(1, 8))

        # --- Projects ---
        projects = self.profile.get("projects", [])
        if projects:
            elements.append(Paragraph("Projects", header_style))
            for proj in projects:
                elements.append(Paragraph(f"<b>{proj.get('title', '')}</b>", normal_style))
                if proj.get("description"):
                    elements.append(Paragraph(proj["description"], bullet_style))
                elements.append(Spacer(1, 6))
            elements.append(Spacer(1, 8))

        # --- Experience ---
        experience = self.profile.get("experience", [])
        if experience:
            elements.append(Paragraph("Experience", header_style))
            for exp in experience:
                elements.append(Paragraph(exp if isinstance(exp, str) else str(exp), bullet_style))
            elements.append(Spacer(1, 8))

        # --- Certifications ---
        certs = self.profile.get("certificates", [])
        if certs:
            elements.append(Paragraph("Certifications", header_style))
            for cert in certs:
                text = cert if isinstance(cert, str) else f"{cert.get('name', '')} - {cert.get('source', '')}"
                elements.append(Paragraph(text, bullet_style))
            elements.append(Spacer(1, 8))

        # --- Build PDF ---
        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer

    # -------------------------
    # 💾 Save to DB (optional)
    # -------------------------
    def save_to_db(self, resume_type="original"):
        """Save resume metadata in SQLite (optional, temporary for session)."""
        try:
            conn = sqlite3.connect(":memory:" if self.use_in_memory else self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    resume_type TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute(
                "INSERT INTO resumes (user_id, resume_type, summary) VALUES (?, ?, ?)",
                (self.user_id, resume_type, self.generated_summary),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Failed to record resume in DB: {e}")
