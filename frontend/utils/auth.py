from datetime import datetime
import streamlit as st
from frontend.utils.database import get_database

def init_session_state():
    """Initialize session state variables"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"

def login_user(email, password):
    """Authenticate user"""
    try:
        db = get_database()
        if not db:
            # Demo mode - allow admin login
            if email == "admin@africanleague.com" and password == "admin123":
                st.session_state.user = {"email": email, "role": "admin"}
                st.session_state.role = "admin"
                return True
            return False
            
        user = db.users.find_one({"email": email, "password": password})
        
        if user:
            st.session_state.user = user
            st.session_state.role = user.get('role', 'visitor')
            return True
        return False
        
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def logout_user():
    """Logout user"""
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.current_page = "Home"

def register_user(email, password, role, country=None):
    """Register new user"""
    try:
        db = get_database()
        if not db:
            # In demo mode, allow registration
            return True
            
        # Check if user already exists
        if db.users.find_one({"email": email}):
            return False
            
        user_data = {
            "email": email,
            "password": password,
            "role": role,
            "created_at": datetime.now()
        }
        
        if country:
            user_data["country"] = country
            
        result = db.users.insert_one(user_data)
        return result.inserted_id is not None
        
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False
