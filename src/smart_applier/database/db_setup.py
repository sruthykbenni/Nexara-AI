import sqlite3
from smart_applier.utils.path_utils import get_data_dirs
from pathlib import Path
import os

def initialize_database():
    """
    Initializes the Smart Applier AI SQLite database.
    Automatically creates all required tables if not present.
    Safe to run multiple times.
    """
    paths = get_data_dirs()
    db_path = paths["root"] / "smart_applier.db"
    os.makedirs(paths["root"], exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
    -- 🧩 Table: profiles
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE,
        name TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        linkedin TEXT,
        github TEXT,
        profile_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 💼 Table: jobs
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT,
        experience TEXT,
        skills TEXT,
        summary TEXT,
        posted_on TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 📄 Table: resumes
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        resume_type TEXT,
        file_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 🎯 Table: top_matched_jobs
    CREATE TABLE IF NOT EXISTS top_matched_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized successfully at: {db_path}")



# ------------------------------
# 🧪 Optional: Load Sample Data (for first-time Cloud use)
# ------------------------------
def load_sample_data():
    """
    Loads a sample profile and job record to make the Streamlit Cloud app non-empty on first run.
    Call this after initialize_database() only if database is empty.
    """
    paths = get_data_dirs()
    db_path = paths["root"] / "smart_applier.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if profiles exist
    cur.execute("SELECT COUNT(*) FROM profiles;")
    count = cur.fetchone()[0]

    if count == 0:
        sample_profile = {
            "personal": {
                "name": "Demo User",
                "email": "demo@example.com",
                "phone": "+91 9999999999",
                "location": "Kerala, India",
                "linkedin": "https://linkedin.com/in/demo",
                "github": "https://github.com/demo",
            },
            "education": ["MSc Computer Science (Data Analytics), Digital University Kerala"],
            "skills": {"Programming": ["Python", "SQL", "Power BI"]},
            "projects": [{"title": "Smart Applier AI", "description": "AI-driven job automation app"}],
            "experience": ["Internship in Data Science"],
            "certificates": [{"name": "Power BI Data Analyst", "source": "Microsoft"}],
            "achievements": ["Published a mini research paper on NLP"]
        }

        cur.execute("""
        INSERT INTO profiles (user_id, name, email, phone, location, linkedin, github, profile_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "demo",
            sample_profile["personal"]["name"],
            sample_profile["personal"]["email"],
            sample_profile["personal"]["phone"],
            sample_profile["personal"]["location"],
            sample_profile["personal"]["linkedin"],
            sample_profile["personal"]["github"],
            str(sample_profile)
        ))

        conn.commit()
        print("🌱 Sample profile inserted successfully.")
    else:
        print("ℹ️ Database already has profiles — skipping sample insert.")

    conn.close()


# ------------------------------
# 🔹 Main entry point
# ------------------------------
if __name__ == "__main__":
    initialize_database()
    # Optional: uncomment below to preload sample data
    # load_sample_data()
