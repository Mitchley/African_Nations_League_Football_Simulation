from pymongo import MongoClient
import streamlit as st
from datetime import datetime

@st.cache_resource
def get_database():
    """Get MongoDB database connection"""
    try:
        # Get MongoDB URI from Streamlit secrets
        mongodb_uri = st.secrets.get("MONGODB_URI", "mongodb://localhost:27017")
        
        client = MongoClient(mongodb_uri)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        return client.african_nations_league
        
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        # Return a mock database for demo purposes
        return None

def save_team(team_data):
    """Save team to database"""
    try:
        db = get_database()
        if db:
            return db.federations.insert_one(team_data)
        return None
    except Exception as e:
        st.error(f"Error saving team: {str(e)}")
        return None

def get_players_by_federation(federation_email):
    """Get players by federation email"""
    try:
        db = get_database()
        if db:
            team = db.federations.find_one({"representative_email": federation_email})
            return team.get('players', []) if team else []
        return []
    except Exception as e:
        st.error(f"Error fetching players: {str(e)}")
        return []

def initialize_database():
    """Initialize database with admin user and collections"""
    try:
        db = get_database()
        if not db:
            print("❌ Database not available - running in demo mode")
            return False
            
        # Create admin user if not exists
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
            print("✅ Admin user created")
        
        # Create indexes
        db.federations.create_index("country", unique=True)
        db.federations.create_index("representative_email", unique=True)
        db.matches.create_index("stage")
        
        print("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False
