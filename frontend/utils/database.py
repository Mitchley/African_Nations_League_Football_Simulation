from pymongo import MongoClient
import streamlit as st
from datetime import datetime

@st.cache_resource
def get_database():
    """Get MongoDB database connection using DATABASE_NAME from secrets"""
    try:
        # Check if secrets are available
        if "MONGODB_URI" not in st.secrets:
            st.error("❌ MONGODB_URI not found in secrets")
            return None
        
        # Get MongoDB URI from secrets
        mongodb_uri = st.secrets["MONGODB_URI"]
        database_name = st.secrets.get("DATABASE_NAME", "AfricanLeague")
        
        # Validate the URI
        if not mongodb_uri or mongodb_uri.strip() == "":
            st.error("❌ MONGODB_URI is empty")
            return None
        
        # Connect to MongoDB
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
        
        # Use the specified database name
        database = client[database_name]
        return database
        
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return None

def save_team(team_data):
    db = get_database()
    if db:
        try:
            return db.federations.insert_one(team_data)
        except Exception as e:
            st.error(f"Error saving team: {str(e)}")
    return None

def get_players_by_federation(federation_email):
    db = get_database()
    if not db:
        return []
    try:
        team = db.federations.find_one({"representative_email": federation_email})
        return team.get('players', []) if team else []
    except Exception as e:
        st.error(f"Error fetching players: {str(e)}")
        return []

def initialize_database():
    db = get_database()
    if not db:
        return False
        
    admin_email = st.secrets.get("ADMIN_EMAIL", "admin@africanleague.com")
    admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    
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
    try:
        return list(db.federations.find({}))
    except Exception as e:
        st.error(f"Error fetching teams: {str(e)}")
        return []

def get_tournament_matches():
    db = get_database()
    if not db:
        return []
    try:
        return list(db.matches.find({}))
    except Exception as e:
        return []

def get_tournament_data():
    db = get_database()
    if not db:
        return {}
    try:
        return db.tournaments.find_one({}) or {}
    except Exception as e:
        return {}
