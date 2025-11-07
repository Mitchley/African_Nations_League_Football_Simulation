import streamlit as st
import time
import random
from datetime import datetime
from frontend.utils.auth import init_session_state, login_user, logout_user
from frontend.utils.database import save_team, get_database, get_players_by_federation, initialize_database
from frontend.utils.match_simulator import simulate_match_with_commentary
from backend.email_service import notify_federations_after_match

init_session_state()

# Country flags dictionary
COUNTRY_FLAGS = {
    "Algeria": "🇩🇿", "Angola": "🇦🇴", "Benin": "🇧🇯", "Botswana": "🇧🇼",
    "Burkina Faso": "🇧🇫", "Burundi": "🇧🇮", "Cameroon": "🇨🇲", "Cape Verde": "🇨🇻",
    "DR Congo": "🇨🇩", "Egypt": "🇪🇬", "Ethiopia": "🇪🇹", "Ghana": "🇬🇭",
    "Ivory Coast": "🇨🇮", "Kenya": "🇰🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿",
    "Nigeria": "🇳🇬", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "Tanzania": "🇹🇿",
    "Tunisia": "🇹🇳", "Uganda": "🇺🇬", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼"
}

AFRICAN_COUNTRIES = list(COUNTRY_FLAGS.keys())

AFRICAN_FIRST_NAMES = ["Mohamed", "Youssef", "Ahmed", "Kofi", "Kwame", "Adebayo", "Tendai", "Blessing", "Ibrahim", "Abdul", "Chinedu", "Faith", "Sipho", "Lerato", "Naledi", "Thabo"]
AFRICAN_LAST_NAMES = ["Diallo", "Traore", "Mensah", "Adebayo", "Okafor", "Mohammed", "Ibrahim", "Kamara", "Sow", "Keita", "Ndiaye", "Conte", "Mbeki", "Zuma", "Mandela", "Toure"]

class Player:
    def __init__(self, name, position, is_captain=False):
        self.name = name
        self.position = position
        self.is_captain = is_captain

def generate_player_name():
    return f"{random.choice(AFRICAN_FIRST_NAMES)} {random.choice(AFRICAN_LAST_NAMES)}"

def generate_player_ratings(position):
    ratings = {}
    for pos in ["GK", "DF", "MD", "AT"]:
        if pos == position:
            ratings[pos] = random.randint(50, 100)  # Natural position
        else:
            ratings[pos] = random.randint(0, 50)    # Non-natural position
    return ratings

def calculate_team_rating(squad):
    if not squad:
        return 75.0
    total_rating = sum(p["ratings"][p["naturalPosition"]] for p in squad)
    return round(total_rating / len(squad), 2)

def main():
    st.set_page_config(
        page_title="African Nations League", 
        layout="wide", 
        page_icon="⚽",
        initial_sidebar_state="expanded"
    )
    
    # Show connection status in sidebar
    with st.sidebar:
        if "MONGODB_URI" in st.secrets:
            st.success("✅ Secrets loaded from Streamlit Cloud")
            db = get_database()
            if db:
                st.success("✅ Connected to MongoDB")
                try:
                    team_count = db.federations.count_documents({})
                    st.info(f"📊 Database has {team_count} teams")
                except:
                    st.info("📊 Checking database...")
            else:
                st.error("❌ Cannot connect to MongoDB")
        else:
            st.error("❌ No secrets found in Streamlit Cloud")
    
    # Initialize database
    initialize_database()
    
    if not st.session_state.user:
        hide_sidebar()
        show_login_page()
    else:
        show_app()

def hide_sidebar():
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

def show_login_page():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 3rem; border-radius: 20px; color: white; text-align: center; margin-bottom: 2rem; border: 4px solid #FFD700;">
        <h1 style="margin:0; color: #FFD700; font-size: 3em;">🏆 AFRICAN NATIONS LEAGUE</h1>
        <p style="margin:0; font-size: 1.5em;">Road to Glory 2025</p>
        <p style="margin:0; font-size: 1em;">INF4001N: 2025 Entrance Exam Brief for 2026</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 **Admin Login**", "🇺🇳 **Federation Sign Up**", "👤 **Visitor Access**"])
    
    with tab1: show_admin_login()
    with tab2: show_federation_registration()
    with tab3: show_visitor_access()

def show_admin_login():
    st.subheader("Admin Login")
    
    with st.form("admin_login_form"):
        email = st.text_input("**Email**", placeholder="admin@africanleague.com")
        password = st.text_input("**Password**", type="password")
        
        if st.form_submit_button("🚀 **Login as Admin**", use_container_width=True):
            if email and password and login_user(email, password):
                st.success("✅ Admin login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid admin credentials")

def show_visitor_access():
    st.subheader("Visitor Access")
    st.info("Explore the tournament as a visitor - no registration required!")
    
    if st.button("👀 **Enter as Visitor**", use_container_width=True, type="primary"):
        st.session_state.user = {"email": "visitor@africanleague.com", "role": "visitor"}
        st.session_state.role = "visitor"
        st.success("🎉 Welcome! Entering as visitor...")
        time.sleep(1)
        st.rerun()

def show_federation_registration():
    st.subheader("🇺🇳 Federation Registration")
    
    db = get_database()
    
    if not db:
        st.error("❌ Database not available. Please check your MongoDB connection.")
        return
    
    # Check current team count
    existing_teams = db.federations.count_documents({})
    
    st.info(f"📊 Current teams in database: {existing_teams}/8")
    
    if existing_teams >= 8:
        st.warning("⚠️ Tournament is full with 8 teams! New registrations will be waitlisted.")
    
    # Initialize session state for squad
    if 'squad' not in st.session_state:
        st.session_state.squad = []
    if 'player_ratings' not in st.session_state:
        st.session_state.player_ratings = {}
    
    squad = st.session_state.squad
    
    # Player addition section
    col1, col2 = st.columns([3, 1])
    with col1:
        player_name = st.text_input("Player Name", placeholder="Enter player name", key="player_name_input")
    with col2:
        pos_count = {'GK': 0, 'DF': 0, 'MD': 0, 'AT': 0}
        for player in squad:
            pos_count[player.position] += 1
        
        available_positions = []
        if pos_count['GK'] < 3: available_positions.append("GK")
        if pos_count['DF'] < 7: available_positions.append("DF")
        if pos_count['MD'] < 8: available_positions.append("MD")
        if pos_count['AT'] < 5: available_positions.append("AT")
        
        position = st.selectbox("Position", available_positions, 
                              disabled=len(available_positions) == 0,
                              key="position_select")
    
    # Add player button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        add_disabled = (len(squad) >= 23 or not player_name or len(available_positions) == 0)
        if st.button("➕ Add Player", disabled=add_disabled, use_container_width=True):
            if player_name and len(squad) < 23:
                ratings = generate_player_ratings(position)
                new_player = Player(player_name, position)
                st.session_state.player_ratings[player_name] = ratings
                st.session_state.squad.append(new_player)
                st.rerun()
    
    # Show current squad status
    st.write(f"**Squad: {len(squad)}/23 players**")
    
    # Show current squad composition
    st.write("### Squad Composition")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Goalkeepers", f"{pos_count['GK']}/3")
    with col2: st.metric("Defenders", f"{pos_count['DF']}/7")
    with col3: st.metric("Midfielders", f"{pos_count['MD']}/8")
    with col4: st.metric("Attackers", f"{pos_count['AT']}/5")
    
    if len(squad) < 23:
        st.warning(f"**Need {23 - len(squad)} more players** (3 GK, 7 DF, 8 MD, 5 AT)")
    
    # Show current squad
    if squad:
        if len(squad) == 23:
            captain_options = [f"{p.name} ({p.position})" for p in squad]
            selected_captain = st.selectbox("Select Captain", captain_options, key="captain_select")
            captain_index = captain_options.index(selected_captain)
            
            for i, player in enumerate(squad):
                player.is_captain = (i == captain_index)
        
        st.write("### Your Squad")
        positions = {
            "GK": "🥅 Goalkeepers",
            "DF": "🛡️ Defenders", 
            "MD": "⚡ Midfielders",
            "AT": "🎯 Attackers"
        }
        
        for pos, title in positions.items():
            position_players = [p for p in squad if p.position == pos]
            if position_players:
                with st.expander(f"{title} ({len(position_players)})"):
                    for player in position_players:
                        captain = " ⭐ CAPTAIN" if player.is_captain else ""
                        if player.name in st.session_state.player_ratings:
                            rating = st.session_state.player_ratings[player.name][player.position]
                            st.write(f"**{player.name}** - Rating: {rating}{captain}")
                        else:
                            st.write(f"**{player.name}**{captain}")
    
    # Clear squad button
    if squad:
        if st.button("🗑️ Clear Squad", key="clear_squad"):
            st.session_state.squad = []
            if 'player_ratings' in st.session_state:
                del st.session_state.player_ratings
            st.rerun()
    
    # Main registration form
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("Country", AFRICAN_COUNTRIES, key="country_select")
            manager = st.text_input("Manager Name", key="manager_input")
        with col2:
            rep_name = st.text_input("Representative Name", key="rep_name_input")
            rep_email = st.text_input("Email", key="rep_email_input")
            password = st.text_input("Password", type="password", key="password_input")
        
        submit_disabled = (len(squad) != 23)
        submitted = st.form_submit_button("🚀 Register Federation", use_container_width=True, disabled=submit_disabled)
        
        if submitted:
            if len(squad) == 23:
                final_pos_count = {'GK': 0, 'DF': 0, 'MD': 0, 'AT': 0}
                for player in squad:
                    final_pos_count[player.position] += 1
                
                if (final_pos_count['GK'] >= 2 and final_pos_count['DF'] >= 6 and 
                    final_pos_count['MD'] >= 6 and final_pos_count['AT'] >= 3):
                    if register_federation(country, manager, rep_name, rep_email, password, squad):
                        st.success("✅ Registered successfully!")
                        if login_user(rep_email, password):
                            st.rerun()
                else:
                    st.error("❌ Invalid squad composition! Need at least: 2 GK, 6 DF, 6 MD, 3 AT")
            else:
                st.error(f"❌ Need {23 - len(squad)} more players to complete squad")

def register_federation(country, manager, rep_name, rep_email, password, squad):
    try:
        db = get_database()
        
        if not db:
            st.error("❌ Database not available")
            return False
        
        # Check duplicates
        if db.users.find_one({"email": rep_email}):
            st.error("❌ Email already registered")
            return False
        
        if db.federations.find_one({"country": country}):
            st.error("❌ Country already registered")
            return False
        
        # Create user
        from frontend.utils.auth import register_user
        if not register_user(rep_email, password, "federation", country):
            st.error("❌ User registration failed")
            return False
        
        # Convert squad to serializable format
        squad_data = []
        for player in squad:
            squad_data.append({
                "name": player.name,
                "naturalPosition": player.position,
                "ratings": st.session_state.player_ratings.get(player.name, generate_player_ratings(player.position)),
                "isCaptain": player.is_captain
            })
        
        # Calculate team rating
        team_rating = calculate_team_rating(squad_data)
        
        # Save team
        team_data = {
            "country": country, 
            "manager": manager, 
            "representative_name": rep_name,
            "representative_email": rep_email, 
            "rating": team_rating, 
            "players": squad_data,
            "points": 0, 
            "registered_at": datetime.now(),
            "status": "active"
        }
        
        result = db.federations.insert_one(team_data)
        
        # Initialize tournament if this is the 8th team
        team_count = db.federations.count_documents({})
        if team_count >= 8:
            initialize_tournament(db)
            st.balloons()
            st.success("🎊 Tournament started with 8 teams!")
        
        if 'squad' in st.session_state:
            del st.session_state.squad
        if 'player_ratings' in st.session_state:
            del st.session_state.player_ratings
            
        return True
        
    except Exception as e:
        st.error(f"❌ Registration error: {str(e)}")
        return False

def initialize_tournament(db):
    """Initialize tournament bracket with 8 teams"""
    teams = list(db.federations.find({}).limit(8))
    
    if len(teams) < 8:
        st.error(f"Need 8 teams to start tournament. Currently have {len(teams)} teams.")
        return
    
    random.shuffle(teams)
    
    # Clear existing matches
    db.matches.delete_many({})
    
    # Create quarter-final matches
    for i in range(0, 8, 2):
        match_data = {
            "teamA_id": teams[i]["_id"],
            "teamA_name": teams[i]["country"],
            "teamA_rating": teams[i]["rating"],
            "teamB_id": teams[i+1]["_id"],
            "teamB_name": teams[i+1]["country"],
            "teamB_rating": teams[i+1]["rating"],
            "stage": "quarterfinal",
            "status": "scheduled",
            "scoreA": 0,
            "scoreB": 0,
            "goal_scorers": [],
            "commentary": [],
            "method": "not_played",
            "created_at": datetime.now()
        }
        db.matches.insert_one(match_data)
    
    # Create tournament document
    tournament_data = {
        "status": "active",
        "current_stage": "quarterfinal",
        "total_teams": 8,
        "started_at": datetime.now()
    }
    db.tournaments.update_one({}, {"$set": tournament_data}, upsert=True)

def show_app():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    with st.sidebar:
        if st.session_state.role == "visitor":
            st.markdown("### 👋 Welcome, Visitor!")
            st.markdown("**Role:** VISITOR")
        else:
            st.markdown(f"### 👋 Welcome, {st.session_state.user['email']}!")
            st.markdown(f"**Role:** {st.session_state.role.upper()}")
        
        st.markdown("---")
        
        if st.session_state.role == "admin":
            pages = ["🏠 Home", "👨‍💼 Admin", "🏆 Tournament", "⚽ Matches", "📊 Statistics"]
        elif st.session_state.role == "federation":
            pages = ["🏠 Home", "🇺🇳 Federation", "🏆 Tournament", "⚽ Matches", "📊 Statistics"]
        else:
            pages = ["🏠 Home", "🏆 Tournament", "⚽ Matches", "📊 Statistics"]
        
        for page in pages:
            if st.button(page, use_container_width=True, 
                        type="primary" if st.session_state.current_page == page else "secondary"):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    show_current_page()

def show_current_page():
    page_mapping = {
        "🏠 Home": show_home,
        "👨‍💼 Admin": show_admin,
        "🇺🇳 Federation": show_federation,
        "🏆 Tournament": show_tournament,
        "⚽ Matches": show_matches,
        "📊 Statistics": show_statistics
    }
    
    page_function = page_mapping.get(st.session_state.current_page, show_home)
    page_function()

def show_home():
    st.title("🏠 African Nations League Dashboard")
    db = get_database()
    
    if not db:
        st.error("❌ Cannot connect to database. Please check your MongoDB connection.")
        return
    
    team_count = db.federations.count_documents({})
    matches = list(db.matches.find({}))
    completed_matches = len([m for m in matches if m.get('status') == 'completed'])
    tournament = db.tournaments.find_one({}) or {}
    
    st.success(f"✅ Connected to database with {team_count} teams!")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Teams", team_count)
    with col2: st.metric("Matches Played", completed_matches)
    with col3: st.metric("Tournament Status", tournament.get('status', 'pending').title())
    with col4: st.metric("Current Stage", tournament.get('current_stage', 'Not Started').title())
    
    st.markdown("---")
    
    # Display all teams from database
    st.subheader("🇺🇳 All Registered Teams")
    teams = list(db.federations.find({}))
    
    if teams:
        cols = st.columns(4)
        for i, team in enumerate(teams):
            with cols[i % 4]:
                flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                rating = team.get('rating', 'N/A')
                manager = team.get('manager', 'Unknown')
                
                st.markdown(f"""
                <div style="border: 2px solid #1E3C72; border-radius: 10px; padding: 10px; margin: 5px; text-align: center; background: white;">
                    <h3 style="margin: 0; font-size: 1.5em;">{flag}</h3>
                    <h4 style="margin: 5px 0; color: #1E3C72;">{team['country']}</h4>
                    <p style="margin: 2px 0; font-size: 0.9em; color: #666;">Rating: {rating}</p>
                    <p style="margin: 2px 0; font-size: 0.8em; color: #888;">Manager: {manager}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No teams found in database")

def show_admin():
    if st.session_state.role != 'admin':
        st.error("🔒 Admin
