# smart_applier/agents/profile_agent.py
import os
import json
import sqlite3
from typing import Optional, List, Dict, Any
from smart_applier.utils.path_utils import get_data_dirs, ensure_database_exists


class UserProfileAgent:
    """
    Manages profile creation, retrieval, and listing.
    Automatically supports both file-based and in-memory SQLite modes.
    """

    def __init__(self):
        paths = get_data_dirs()
        self.use_in_memory = paths["use_in_memory_db"]
        self.db_path = paths["db_path"]

        # Ensure DB and tables exist if using file-backed DB
        if not self.use_in_memory:
            ensure_database_exists()

    # ------------------------------
    # 🔗 Database connection helper
    # ------------------------------
    def _get_connection(self):
        if self.use_in_memory:
            # Each session will have its own isolated in-memory DB
            conn = sqlite3.connect(":memory:")
            # Initialize tables for this session
            from smart_applier.database.db_setup import create_tables
            create_tables(conn)
            return conn
        else:
            return sqlite3.connect(self.db_path)

    # ------------------------------
    # 💾 Save / Update profile
    # ------------------------------
    def save_profile(self, profile_data: Dict[str, Any], user_id: str) -> str:
        """
        Save or update full profile JSON for the given user_id.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        profile_json = json.dumps(profile_data, indent=2)
        name = profile_data.get("personal", {}).get("name", "")
        email = profile_data.get("personal", {}).get("email", "")

        cursor.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()

        if existing:
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
        return f"session://profiles/{user_id}"

    # ------------------------------
    # 📥 Load profile
    # ------------------------------
    def load_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the full profile JSON for the given user_id.
        Returns None if not found.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT profile_json FROM profiles WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        else:
            return None

    # ------------------------------
    # 📋 List all profiles
    # ------------------------------
    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        Return a list of all profile metadata (name, email, user_id).
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, email, created_at FROM profiles")
        rows = cursor.fetchall()
        conn.close()

        return [
            {"user_id": r[0], "name": r[1], "email": r[2], "created_at": r[3]} for r in rows
        ]
