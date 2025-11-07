from pymongo import MongoClient
import streamlit as st
from datetime import datetime

@st.cache_resource
def get_database():
    """Get MongoDB database connection - reads from Streamlit Cloud secrets"""
    try:
        # This reads from Streamlit Cloud secrets
        mongodb_uri = st.secrets["MONGODB_URI"]
        
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            retryWrites=True,
            w="majority"
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        
        # Use database from connection string
        return client.get_database()
        
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return None

def save_team(team_data):
    db = get_database()
    if db:
        return db.federations.insert_one(team_data)
    return None

def get_players_by_federation(federation_email):
    db = get_database()
    if not db:
        return []
    team = db.federations.find_one({"representative_email": federation_email})
    return team.get('players', []) if team else []

def initialize_database():
    db = get_database()
    if not db:
        return False
        
    # Get admin credentials from Streamlit secrets
    admin_email = st.secrets["ADMIN_EMAIL"]
    admin_password = st.secrets["ADMIN_PASSWORD"]
    
    existing_admin = db.users.find_one({"email": admin_email})
    if not existing_admin:
        db.users.insert_one({
            "email": admin_email,
            "password": admin_password,
            "role": "admin",
            "created_at": datetime.now()
        })
    
    return True

def get_all_teams():
    db = get_database()
    if not db:
        return []
    return list(db.federations.find({}))

def get_tournament_matches():
    db = get_database()
    if not db:
        return []
    return list(db.matches.find({}))

def get_tournament_data():
    db = get_database()
    if not db:
        return {}
    return db.tournaments.find_one({}) or {}
