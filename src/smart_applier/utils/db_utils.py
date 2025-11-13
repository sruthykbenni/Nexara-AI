import sqlite3
import json
from pathlib import Path
from smart_applier.utils.path_utils import get_data_dirs


# -----------------------------
# Database setup & connection
# -----------------------------
def get_db_path() -> Path:
    """Return database file path (data/smart_applier.db)."""
    data_dirs = get_data_dirs()
    db_path = data_dirs["root"] / "smart_applier.db"
    db_path.touch(exist_ok=True)
    return db_path


def get_connection():
    """Create and return a SQLite connection."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Profile CRUD
# -----------------------------
def insert_profile(user_id: str, profile_data: dict):
    """Insert or update user profile."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO profiles (user_id, name, email, phone, location, linkedin, github, data_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            email = excluded.email,
            phone = excluded.phone,
            location = excluded.location,
            linkedin = excluded.linkedin,
            github = excluded.github,
            data_json = excluded.data_json
    """, (
        user_id,
        profile_data.get("personal", {}).get("name"),
        profile_data.get("personal", {}).get("email"),
        profile_data.get("personal", {}).get("phone"),
        profile_data.get("personal", {}).get("location"),
        profile_data.get("personal", {}).get("linkedin"),
        profile_data.get("personal", {}).get("github"),
        json.dumps(profile_data),
    ))

    conn.commit()
    conn.close()


def get_all_profiles():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, name, email, phone, location, linkedin, github, created_at
        FROM profiles ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# -----------------------------
# Job CRUD
# -----------------------------
def insert_job(job_data: dict):
    """Insert a single job posting."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO jobs (title, company, location, skills, summary, posted_on)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        job_data.get("Title"),
        job_data.get("Company"),
        job_data.get("Location"),
        job_data.get("Skills"),
        job_data.get("Summary"),
        job_data.get("Posted On"),
    ))
    conn.commit()
    conn.close()


def get_all_jobs(limit: int = 100):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, company, location, skills, summary, posted_on, created_at
        FROM jobs ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# -----------------------------
# Resume CRUD
# -----------------------------
def insert_resume(user_id: str, resume_type: str, file_path: str):
    """Insert new resume record."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resumes (user_id, type, file_path)
        VALUES (?, ?, ?)
    """, (user_id, resume_type, file_path))
    conn.commit()
    conn.close()


def get_all_resumes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, type, file_path, created_at
        FROM resumes ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# -----------------------------
# Initialize Tables
# -----------------------------
def initialize_tables():
    """Create necessary tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    # Profiles table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE,
        name TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        linkedin TEXT,
        github TEXT,
        data_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Jobs table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT,
        skills TEXT,
        summary TEXT,
        posted_on TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Resumes table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        type TEXT,
        file_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
# src/smart_applier/utils/db_utils.py
import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from smart_applier.utils.path_utils import get_data_dirs
from smart_applier.database.db_setup import initialize_database


# -------------------------
# 🔗 DB Connection
# -------------------------
def get_connection():
    """Return a SQLite connection (in-memory or persistent)."""
    paths = get_data_dirs()
    db_path = paths["db_path"]

    # If using Streamlit in-memory mode, rebuild schema every session
    if paths.get("use_in_memory_db", False):
        conn = sqlite3.connect(":memory:")
        initialize_database(conn)
    else:
        if not os.path.exists(db_path):
            initialize_database()
        conn = sqlite3.connect(db_path)
    return conn


# -------------------------
# 🧩 Profile Operations
# -------------------------
def insert_or_update_profile(user_id: str, profile_data: dict):
    """Insert or update a user profile JSON."""
    conn = get_connection()
    cursor = conn.cursor()

    profile_json = json.dumps(profile_data, indent=2)
    name = profile_data.get("personal", {}).get("name", "")
    email = profile_data.get("personal", {}).get("email", "")

    cursor.execute("SELECT id FROM profiles WHERE user_id=?", (user_id,))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE profiles SET name=?, email=?, profile_json=? WHERE user_id=?",
            (name, email, profile_json, user_id),
        )
    else:
        cursor.execute(
            "INSERT INTO profiles (user_id, name, email, profile_json) VALUES (?, ?, ?, ?)",
            (user_id, name, email, profile_json),
        )

    conn.commit()
    conn.close()


def get_profile(user_id: str) -> Optional[dict]:
    """Fetch full profile JSON for a given user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_json FROM profiles WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None


def list_profiles() -> List[Dict[str, Any]]:
    """Return list of profiles metadata."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, created_at FROM profiles")
    rows = cursor.fetchall()
    conn.close()
    return [{"user_id": r[0], "name": r[1], "email": r[2], "created_at": r[3]} for r in rows]


# -------------------------
# 💼 Job Operations
# -------------------------
def bulk_insert_jobs(jobs: List[Dict[str, Any]]):
    """Bulk insert job postings."""
    conn = get_connection()
    cursor = conn.cursor()
    for job in jobs:
        cursor.execute("""
            INSERT INTO scraped_jobs (title, company, location, experience, skills, summary, posted_on)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job.get("Title") or job.get("title"),
            job.get("Company") or job.get("company"),
            job.get("Location") or job.get("location"),
            job.get("Experience") or job.get("experience"),
            job.get("Skills") or job.get("skills"),
            job.get("Summary") or job.get("summary"),
            job.get("Posted On") or job.get("posted_on"),
        ))
    conn.commit()
    conn.close()


def get_all_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent jobs from DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scraped_jobs ORDER BY id DESC LIMIT ?", (limit,))
    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


# -------------------------
# 🧠 Matching Results
# -------------------------
def insert_top_matched(job_id: int, score: float):
    """Store top matched job and score."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO top_matched_jobs (job_id, score) VALUES (?, ?)",
        (job_id, score),
    )
    conn.commit()
    conn.close()


def get_latest_top_matched(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch latest top matched jobs joined with job details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.*, t.score
        FROM top_matched_jobs t
        JOIN scraped_jobs j ON t.job_id = j.id
        ORDER BY t.id DESC
        LIMIT ?
    """, (limit,))
    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


# -------------------------
# 📄 Resume Storage
# -------------------------
def insert_resume(user_id: str, resume_type: str, file_path: str):
    """Record resume metadata."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resumes (user_id, resume_type, file_path)
        VALUES (?, ?, ?)
    """, (user_id, resume_type, file_path))
    conn.commit()
    conn.close()
