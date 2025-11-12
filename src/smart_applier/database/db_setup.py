# src/smart_applier/database/db_setup.py
import sqlite3
from smart_applier.utils.path_utils import get_data_dirs


def create_tables(conn=None):
    """
    Creates all necessary tables for Smart Applier AI.
    Runs safely even if tables already exist.
    """
    paths = get_data_dirs()
    db_path = paths["db_path"]

    if conn is None:
        conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # -------------------------
    # 🧩 PROFILES TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            name TEXT,
            email TEXT,
            profile_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # 💼 SCRAPED JOBS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraped_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            experience TEXT,
            skills TEXT,
            summary TEXT,
            posted_on TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # 🧠 TOP MATCHED JOBS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS top_matched_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES scraped_jobs(id)
        )
    """)

    # -------------------------
    # 📄 RESUMES TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            resume_type TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES profiles(user_id)
        )
    """)

    # -------------------------
    # ✨ TAILORED SESSIONS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tailored_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            coverage_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database tables verified / created successfully!")
