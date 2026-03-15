import sqlite3
import uuid
from datetime import datetime

DB_NAME = "medic_check.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            allergies TEXT,
            conditions TEXT,
            emergency_contact TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generate_user_id():
    short_id = uuid.uuid4().hex[:6].upper()
    return f"MC-{short_id}"

def insert_user(name, blood_group, allergies, conditions, emergency_contact):
    user_id = generate_user_id()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (id, name, blood_group, allergies, conditions, emergency_contact, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, name, blood_group, allergies, conditions, emergency_contact, datetime.now()))
    conn.commit()
    conn.close()
    return user_id

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None