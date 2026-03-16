import sqlite3
import uuid
from datetime import datetime

def init_db():
    conn = sqlite3.connect("medic_check.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            blood_group TEXT,
            allergies TEXT,
            conditions TEXT,
            emergency_contact TEXT,
            registered_on TEXT
        )
    """)
    
    # Check if registered_on column exists, if not add it
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if "registered_on" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN registered_on TEXT")
        # Update existing rows with a default value
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE users SET registered_on = ? WHERE registered_on IS NULL", (current_time,))
    
    conn.commit()
    conn.close()

def register_user(name, blood_group, emergency_contact, allergies, conditions):
    conn = sqlite3.connect("medic_check.db")
    cursor = conn.cursor()
    user_id = f"MC-{str(uuid.uuid4())[:8].upper()}"
    registered_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, name, blood_group, allergies, conditions, emergency_contact, registered_on)
    )
    conn.commit()
    conn.close()
    return user_id

def get_user(user_id):
    conn = sqlite3.connect("medic_check.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, blood_group, allergies, conditions, emergency_contact, registered_on FROM users WHERE id = ?", (user_id,))
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
            "created_at": row[6]
        }
    return None

# alias for compatibility
insert_user = register_user