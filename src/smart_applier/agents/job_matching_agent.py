# smart_applier/agents/job_matching_agent.py
import pandas as pd
import numpy as np
import string
import faiss
from sentence_transformers import SentenceTransformer
from typing import Dict, Any
from smart_applier.utils.path_utils import get_data_dirs, ensure_database_exists


class JobMatchingAgent:
    """
    Performs semantic job matching between a user's profile and scraped jobs.
    Works fully in memory — Streamlit Cloud / session safe.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        paths = get_data_dirs()
        self.use_in_memory = paths["use_in_memory_db"]
        self.db_path = paths["db_path"]

        # Ensure DB ready for local mode
        if not self.use_in_memory:
            ensure_database_exists()

    # ------------------------------
    # 🔹 Text Preprocessing
    # ------------------------------
    @staticmethod
    def preprocess_text(text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        return " ".join(text.split())

    # ------------------------------
    # 🧩 Embed user profile
    # ------------------------------
    def embed_user_profile(self, profile: Dict[str, Any]) -> np.ndarray:
        """
        Convert user's profile (skills, projects, achievements) into an embedding vector.
        """
        skills_text = " ".join(
            [skill for sublist in profile.get("skills", {}).values() for skill in sublist]
        )
        projects_text = " ".join(
            [p.get("title", "") + " " + p.get("description", "") for p in profile.get("projects", [])]
        )
        achievements_text = " ".join(profile.get("achievements", []))

        combined = " ".join([skills_text, projects_text, achievements_text])
        combined = self.preprocess_text(combined)
        vector = self.model.encode(combined, convert_to_numpy=True)
        return vector

    # ------------------------------
    # 📄 Embed job descriptions
    # ------------------------------
    def embed_jobs(self, jobs_df: pd.DataFrame) -> np.ndarray:
        job_texts = []
        for _, row in jobs_df.iterrows():
            skills = row.get("skills") or row.get("Skills") or ""
            summary = row.get("summary") or row.get("Summary") or ""
            text = skills if skills else summary
            job_texts.append(self.preprocess_text(text))
        if not job_texts:
            return np.empty((0, 384))  # empty embedding placeholder
        embeddings = self.model.encode(job_texts, convert_to_numpy=True)
        return embeddings

    # ------------------------------
    # ⚡ Build FAISS index
    # ------------------------------
    def build_faiss_index(self, job_embeddings: np.ndarray):
        d = job_embeddings.shape[1]
        index = faiss.IndexFlatIP(d)
        faiss.normalize_L2(job_embeddings)
        index.add(job_embeddings)
        return index

    # ------------------------------
    # 🎯 Match jobs for profile
    # ------------------------------
    def match_jobs(
        self, profile_vector: np.ndarray, jobs_df: pd.DataFrame, job_embeddings: np.ndarray, top_k: int = 10
    ) -> pd.DataFrame:
        """
        Return top-matched jobs as a DataFrame with similarity scores.
        """
        if job_embeddings.shape[0] == 0:
            raise ValueError("❌ No job embeddings available. Please scrape jobs first.")

        faiss.normalize_L2(profile_vector.reshape(1, -1))
        index = self.build_faiss_index(job_embeddings)
        D, I = index.search(profile_vector.reshape(1, -1), top_k)

        matched = jobs_df.iloc[I[0]].copy()
        matched["match_score"] = np.round(D[0], 4)
        matched.reset_index(drop=True, inplace=True)
        return matched

    # ------------------------------
    # 💾 Optional: cache to DB (session-safe)
    # ------------------------------
    def save_top_matches(self, matched_df: pd.DataFrame):
        """
        Optional helper to persist top matched jobs to SQLite (used in session only).
        """
        import sqlite3

        if self.use_in_memory:
            conn = sqlite3.connect(":memory:")
            from smart_applier.database.db_setup import create_tables
            create_tables(conn)
        else:
            conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS top_matched_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                company TEXT,
                location TEXT,
                skills TEXT,
                match_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        for _, row in matched_df.iterrows():
            cursor.execute("""
                INSERT INTO top_matched_jobs (title, company, location, skills, match_score)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row.get("title"),
                row.get("company"),
                row.get("location"),
                row.get("skills"),
                row.get("match_score"),
            ))

        conn.commit()
        conn.close()
