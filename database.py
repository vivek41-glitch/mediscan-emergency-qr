import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    pass  # Supabase table already created

def register_user(name, blood_group, emergency_contact, allergies, conditions):
    data = {
        "name": name,
        "blood_group": blood_group,
        "emergency_contact": emergency_contact,
        "allergies": allergies,
        "conditions": conditions
    }
    result = supabase.table("medical_profiles").insert(data).execute()
    return result.data[0]["id"]

def get_user(user_id):
    result = supabase.table("medical_profiles").select("*").eq("id", user_id).execute()
    if result.data:
        return result.data[0]
    return None