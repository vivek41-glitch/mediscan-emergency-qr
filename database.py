import sqlite3
import uuid
from datetime import datetime

DB_NAME = "medic_check.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            blood_group TEXT,
            allergies TEXT,
            conditions TEXT,
            emergency_contact TEXT,
            created_at TIMESTAMP,
            registered_on TEXT
        )
    """)

    # Ensure both timestamp columns exist (for old DBs)
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if "created_at" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
    if "registered_on" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN registered_on TEXT")

    conn.commit()
    conn.close()

def register_user(name, blood_group, emergency_contact, allergies, conditions):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user_id = f"MC-{str(uuid.uuid4())[:8].upper()}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """INSERT INTO users (id, name, blood_group, allergies, conditions,
           emergency_contact, created_at, registered_on)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, name, blood_group, allergies, conditions, emergency_contact, now, now)
    )
    conn.commit()
    conn.close()
    return user_id

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, name, blood_group, allergies, conditions,
           emergency_contact, created_at, registered_on
           FROM users WHERE id = ?""",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "blood_group": row[2],
            "allergies": row[3],
            "conditions": row[4],
            "emergency_contact": row[5],
            "created_at": row[6] or row[7] or "N/A",
        }
    return None

# alias for compatibility
insert_user = register_user