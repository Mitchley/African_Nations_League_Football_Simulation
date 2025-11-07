from pymongo import MongoClient
import streamlit as st
from datetime import datetime

@st.cache_resource
def get_database():
    """Get MongoDB database connection with detailed debugging"""
    try:
        # Check if MONGODB_URI exists in secrets
        if "MONGODB_URI" not in st.secrets:
            st.error("❌ MONGODB_URI not found in Streamlit Cloud secrets!")
            return None
        
        # Get the actual MongoDB URI
        mongodb_uri = st.secrets["MONGODB_URI"]
        database_name = st.secrets.get("DATABASE_NAME", "AfricanLeague")
        
        # Check if it's still the placeholder
        if "add_real_mongodb_uri" in mongodb_uri.lower() or "placeholder" in mongodb_uri.lower():
            st.error("❌ PLACEHOLDER DETECTED: You're still using placeholder text!")
            return None
        
        # Validate it's a proper MongoDB URI
        if not mongodb_uri.startswith("mongodb"):
            st.error(f"❌ Invalid MongoDB URI format")
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
        
        # Use the specified database
        database = client[database_name]
        
        return database
        
    except Exception as e:
        st.error(f"❌ MongoDB connection failed: {str(e)}")
        return None

def is_database_available():
    """Check if database is available without causing boolean errors"""
    try:
        db = get_database()
        if db is None:
            return False
        # Test with a simple operation
        db.command('ping')
        return True
    except:
        return False

def save_team(team_data):
    db = get_database()
    if db is not None:
        try:
            return db.federations.insert_one(team_data)
        except Exception as e:
            st.error(f"Error saving team: {str(e)}")
    return None

def get_players_by_federation(federation_email):
    db = get_database()
    if db is None:
        return []
    try:
        team = db.federations.find_one({"representative_email": federation_email})
        return team.get('players', []) if team else []
    except Exception as e:
        st.error(f"Error fetching players: {str(e)}")
        return []

def initialize_database():
    db = get_database()
    if db is None:
        return False
        
    admin_email = st.secrets.get("ADMIN_EMAIL", "admin@africanleague.com")
    admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    
    try:
        existing_admin = db.users.find_one({"email": admin_email})
        if not existing_admin:
            db.users.insert_one({
                "email": admin_email,
                "password": admin_password,
                "role": "admin",
                "created_at": datetime.now()
            })
        return True
    except Exception as e:
        print(f"Admin setup note: {e}")
        return True

def get_all_teams():
    db = get_database()
    if db is None:
        return []
    try:
        return list(db.federations.find({}))
    except Exception as e:
        st.error(f"Error fetching teams: {str(e)}")
        return []

def get_tournament_matches():
    db = get_database()
    if db is None:
        return []
    try:
        return list(db.matches.find({}))
    except Exception as e:
        return []

def get_tournament_data():
    db = get_database()
    if db is None:
        return {}
    try:
        return db.tournaments.find_one({}) or {}
    except Exception as e:
        return {}

def get_team_count():
    """Safely get team count"""
    db = get_database()
    if db is None:
        return 0
    try:
        return db.federations.count_documents({})
    except:
        return 0
