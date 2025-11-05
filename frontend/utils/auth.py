import streamlit as st
from pymongo import MongoClient

def get_database():
    connection_string = "mongodb+srv://mitchleytapiwa2_db_user:D6Zr2jDQhUUmQh0L@cluster0.yp01ize.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(connection_string)
    return client['AfricanLeague']

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = 'visitor'
    # Note: 'teams' session state is initialized in app.py to avoid circular imports

def login_user(email, password):
    db = get_database()
    user = db.users.find_one({"email": email, "password": password})
    if user:
        st.session_state.user = user
        st.session_state.role = user['role']
        return True
    return False

def logout_user():
    st.session_state.user = None
    st.session_state.role = 'visitor'
    # Clear teams from session state if it exists
    if 'teams' in st.session_state:
        st.session_state.teams = []

def get_current_user():
    return st.session_state.user
