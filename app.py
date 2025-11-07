import streamlit as st
import time
import random
from datetime import datetime
from frontend.utils.auth import init_session_state, login_user, logout_user, register_user
from frontend.utils.database import get_database, initialize_database, is_database_available, get_team_count
from frontend.utils.match_simulator import simulate_match_with_commentary

# Initialize
init_session_state()
st.set_page_config(page_title="African Nations League", layout="wide", page_icon="⚽")

# Country flags
COUNTRY_FLAGS = {
    "Algeria": "🇩🇿", "Angola": "🇦🇴", "Benin": "🇧🇯", "Botswana": "🇧🇼",
    "Burkina Faso": "🇧🇫", "Burundi": "🇧🇮", "Cameroon": "🇨🇲", "Cape Verde": "🇨🇻",
    "DR Congo": "🇨🇩", "Egypt": "🇪🇬", "Ethiopia": "🇪🇹", "Ghana": "🇬🇭",
    "Ivory Coast": "🇨🇮", "Kenya": "🇰🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿",
    "Nigeria": "🇳🇬", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "Tanzania": "🇹🇿",
    "Tunisia": "🇹🇳", "Uganda": "🇺🇬", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼"
}

AFRICAN_COUNTRIES = list(COUNTRY_FLAGS.keys())

# Professional CSS
st.markdown("""
<style>
.tournament-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    border: 4px solid #FFD700;
}
.stage-column {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem;
    border: 2px solid #dee2e6;
}
.match-card {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #1E3C72;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.winner-card {
    background: linear-gradient(135deg, #FFD700 0%, #FFEC8B 100%);
    border: 3px solid #1E3C72;
}
.team-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.5rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.2rem;
}
</style>
""", unsafe_allow_html=True)

class Player:
    def __init__(self, name, position, is_captain=False):
        self.name = name
        self.position = position
        self.is_captain = is_captain

def generate_player_name():
    first_names = ["Mohamed", "Youssef", "Ahmed", "Kofi", "Kwame", "Adebayo", "Tendai", "Blessing"]
    last_names = ["Diallo", "Traore", "Mensah", "Adebayo", "Okafor", "Mohammed", "Kamara", "Sow"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_player_ratings(position):
    ratings = {}
    for pos in ["GK", "DF", "MD", "AT"]:
        if pos == position:
            ratings[pos] = random.randint(50, 100)
        else:
            ratings[pos] = random.randint(0, 50)
    return ratings

def calculate_team_rating(squad):
    if not squad:
        return 75.0
    total_rating = sum(p["ratings"][p["naturalPosition"]] for p in squad)
    return round(total_rating / len(squad), 2)

def safe_get_database():
    """Safely get database connection with error handling"""
    try:
        db = get_database()
        if db is None:
            st.error("❌ Database connection failed. Please check your MongoDB connection.")
            return None
        return db
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")
        return None

def main():
    try:
        initialize_database()
        
        if not st.session_state.get('user'):
            show_login_page()
        else:
            show_app()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please check your database connection and try again.")

def show_login_page():
    st.markdown("""
    <div class="tournament-header">
        <h1 style="margin:0; color: #FFD700; font-size: 2.5em;">🏆 AFRICAN NATIONS LEAGUE</h1>
        <p style="margin:0; font-size: 1.3em;">Road to Glory 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Admin Login", "🇺🇳 Federation Sign Up", "👤 Visitor Access"])
    
    with tab1:
        st.subheader("Administrator Login")
        with st.form("admin_login"):
            email = st.text_input("Email", placeholder="admin@africanleague.com")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login as Admin"):
                if login_user(email, password):
                    st.success("Welcome Admin!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        st.subheader("Federation Registration")
        show_federation_registration()
    
    with tab3:
        st.subheader("Visitor Access")
        st.info("Explore tournament matches and standings")
        if st.button("Enter as Visitor"):
            st.session_state.user = {"email": "visitor", "role": "visitor"}
            st.session_state.role = "visitor"
            st.rerun()

def show_federation_registration():
    db = safe_get_database()
    if db is None:
        st.error("Cannot access database. Please try again later.")
        return
    
    try:
        team_count = db.federations.count_documents({})
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        team_count = 0
    
    st.info(f"Teams registered: {team_count}/8")
    
    if team_count >= 8:
        st.warning("Tournament full! New registrations will be waitlisted.")
    
    with st.form("register_team"):
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("Select Country", AFRICAN_COUNTRIES)
            manager = st.text_input("Manager Name")
        with col2:
            rep_name = st.text_input("Representative Name")
            rep_email = st.text_input("Email")
            password = st.text_input("Password", type="password")
        
        # Quick squad generation (meets requirements)
        if st.checkbox("Auto-generate squad (23 players)"):
            st.info("Squad will be auto-generated with proper positions and ratings")
        
        if st.form_submit_button("Register Federation"):
            if register_federation(country, manager, rep_name, rep_email, password):
                st.success("Federation registered successfully!")
                if login_user(rep_email, password):
                    st.rerun()

def register_federation(country, manager, rep_name, rep_email, password):
    try:
        db = safe_get_database()
        if db is None:
            st.error("Database unavailable")
            return False
            
        if db.federations.find_one({"country": country}):
            st.error("Country already registered")
            return False
        
        if not register_user(rep_email, password, "federation", country):
            st.error("Registration failed")
            return False
        
        # Auto-generate squad (meets requirements)
        squad = []
        positions = {"GK": 3, "DF": 7, "MD": 8, "AT": 5}
        for pos, count in positions.items():
            for i in range(count):
                player = {
                    "name": generate_player_name(),
                    "naturalPosition": pos,
                    "ratings": generate_player_ratings(pos),
                    "isCaptain": False
                }
                squad.append(player)
        
        # Make first player captain
        if squad:
            squad[0]["isCaptain"] = True
        
        team_data = {
            "country": country,
            "manager": manager,
            "representative_name": rep_name,
            "representative_email": rep_email,
            "rating": calculate_team_rating(squad),
            "players": squad,
            "registered_at": datetime.now()
        }
        
        db.federations.insert_one(team_data)
        
        # Start tournament if 8 teams reached
        try:
            if db.federations.count_documents({}) >= 8:
                initialize_tournament(db)
                st.balloons()
                st.success("🎊 Tournament started with 8 teams!")
        except Exception as e:
            st.error(f"Tournament start failed: {str(e)}")
        
        return True
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def show_app():
    # Sidebar navigation
    with st.sidebar:
        st.write(f"**Welcome, {st.session_state.user['email']}**")
        st.write(f"Role: {st.session_state.role.upper()}")
        st.markdown("---")
        
        # Role-based navigation
        if st.session_state.role == "admin":
            pages = ["🏠 Dashboard", "🏆 Tournament Bracket", "⚽ Match Control", "📊 Analytics"]
        elif st.session_state.role == "federation":
            pages = ["🏠 Dashboard", "🏆 Tournament Bracket", "👥 My Team", "📊 Statistics"]
        else:
            pages = ["🏠 Dashboard", "🏆 Tournament Bracket", "📊 Statistics"]
        
        for page in pages:
            if st.button(page, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            logout_user()
            st.rerun()
    
    # Show current page
    current_page = st.session_state.get('current_page', '🏠 Dashboard')
    
    if current_page == "🏠 Dashboard":
        show_dashboard()
    elif current_page == "🏆 Tournament Bracket":
        show_tournament_bracket()
    elif current_page == "⚽ Match Control":
        show_match_control()
    elif current_page == "👥 My Team":
        show_my_team()
    elif current_page == "📊 Analytics":
        show_analytics()
    elif current_page == "📊 Statistics":
        show_statistics()

def show_dashboard():
    st.title("🏠 African Nations League Dashboard")
    db = safe_get_database()
    
    if db is None:
        st.error("Database connection failed")
        return
    
    try:
        team_count = db.federations.count_documents({})
        matches = list(db.matches.find({}))
        completed_matches = len([m for m in matches if m.get('status') == 'completed'])
        tournament = db.tournaments.find_one({}) or {}
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Teams", team_count)
    with col2: st.metric("Matches Played", completed_matches)
    with col3: st.metric("Tournament Status", tournament.get('status', 'Not Started').title())
    with col4: st.metric("Current Stage", tournament.get('current_stage', 'Quarter Finals').title())
    
    st.markdown("---")
    
    # Tournament Preview
    st.subheader("🎯 Tournament Overview")
    show_tournament_preview(db)
    
    # Quick Actions for Admin
    if st.session_state.role == 'admin':
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start Tournament", use_container_width=True) and team_count >= 8:
                initialize_tournament(db)
                st.rerun()
        with col2:
            if st.button("⚡ Simulate All", use_container_width=True):
                simulate_all_matches(db)
                st.rerun()

def show_tournament_preview(db):
    try:
        matches = list(db.matches.find({}))
    except Exception as e:
        st.error(f"Error loading matches: {str(e)}")
        return
    
    if not matches:
        st.info("Tournament not started. Register 8 teams to begin.")
        # Show registered teams
        try:
            teams = list(db.federations.find({}))
            if teams:
                st.write("**Registered Teams:**")
                cols = st.columns(4)
                for i, team in enumerate(teams):
                    with cols[i % 4]:
                        flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                        st.markdown(f'<div class="team-badge">{flag} {team["country"]}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading teams: {str(e)}")
        return
    
    # Show bracket preview
    col1, col2, col3 = st.columns(3)
    
    stages = {'quarterfinal': 'QUARTER FINALS', 'semifinal': 'SEMI FINALS', 'final': 'FINAL'}
    
    for stage, title in stages.items():
        stage_matches = [m for m in matches if m.get('stage') == stage]
        if stage_matches:
            col = col1 if stage == 'quarterfinal' else col2 if stage == 'semifinal' else col3
            with col:
                st.subheader(title)
                for match in stage_matches:
                    display_match_preview(match)

def display_match_preview(match):
    flag_a = COUNTRY_FLAGS.get(match['teamA_name'], "🏴")
    flag_b = COUNTRY_FLAGS.get(match['teamB_name'], "🏴")
    
    if match.get('status') == 'completed':
        st.success(f"{flag_a} {match['teamA_name']} {match['scoreA']}-{match['scoreB']} {match['teamB_name']} {flag_b}")
    else:
        st.info(f"{flag_a} {match['teamA_name']} vs {match['teamB_name']} {flag_b}")

def show_tournament_bracket():
    st.markdown("""
    <div class="tournament-header">
        <h1 style="margin:0; color: #FFD700; font-size: 2.5em;">🏆 AFRICAN NATIONS LEAGUE 2025</h1>
        <p style="margin:0; font-size: 1.3em; font-weight: bold;">ROAD TO THE FINAL</p>
    </div>
    """, unsafe_allow_html=True)
    
    db = safe_get_database()
    if db:
        show_full_tournament_bracket(db)

def show_full_tournament_bracket(db):
    try:
        matches = list(db.matches.find({}))
    except Exception as e:
        st.error(f"Error loading tournament data: {str(e)}")
        return
    
    if not matches:
        st.info("🎯 Tournament not started. Admin can start when 8 teams are registered.")
        return
    
    # Three column layout for tournament progression
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        show_stage_matches(matches, "quarterfinal", "QUARTER FINALS")
    
    with col2:
        show_stage_matches(matches, "semifinal", "SEMI FINALS")
    
    with col3:
        show_stage_matches(matches, "final", "GRAND FINAL")
        show_champion(matches)

def show_stage_matches(matches, stage, title):
    stage_matches = [m for m in matches if m.get('stage') == stage]
    
    st.markdown(f"<div class='stage-column'><h3>{title}</h3></div>", unsafe_allow_html=True)
    
    if not stage_matches:
        st.info("⏳ Waiting for previous round...")
        return
    
    for match in stage_matches:
        display_match_card(match)

def display_match_card(match):
    flag_a = COUNTRY_FLAGS.get(match['teamA_name'], "🏴")
    flag_b = COUNTRY_FLAGS.get(match['teamB_name'], "🏴")
    
    if match.get('status') == 'completed':
        winner_bg = "background: #d4edda;" if match['scoreA'] > match['scoreB'] else "background: #f8f9fa;"
        st.markdown(f"""
        <div class="match-card" style="{winner_bg}">
            <div style="display: flex; justify-content: space-between; align-items: center; font-weight: bold;">
                <span>{flag_a} {match['teamA_name']}</span>
                <span>{match['scoreA']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                <span>{flag_b} {match['teamB_name']}</span>
                <span>{match['scoreB']}</span>
            </div>
            <div style="text-align: center; margin-top: 8px; font-size: 0.8em; color: #666;">
                ✅ {match.get('method', 'simulated').title()}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show advancement
        if match.get('stage') != 'final':
            winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
            st.caption(f"➡️ Advances: **{winner}**")
            
    else:
        st.markdown(f"""
        <div class="match-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold;">{flag_a} {match['teamA_name']}</span>
                <span>VS</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                <span style="font-weight: bold;">{flag_b} {match['teamB_name']}</span>
                <span>⏰</span>
            </div>
            <div style="text-align: center; margin-top: 8px; font-size: 0.8em; color: #666;">
                Scheduled
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Match controls for admin
        if st.session_state.role == 'admin':
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🎮 Play", key=f"play_{match['_id']}"):
                    play_match_with_commentary(match)
            with col2:
                if st.button(f"⚡ Simulate", key=f"sim_{match['_id']}"):
                    simulate_match_quick(match)

def show_champion(matches):
    final_matches = [m for m in matches if m.get('stage') == 'final' and m.get('status') == 'completed']
    
    if final_matches:
        final = final_matches[0]
        winner = final['teamA_name'] if final['scoreA'] > final['scoreB'] else final['teamB_name']
        flag = COUNTRY_FLAGS.get(winner, "🏆")
        
        st.markdown(f"""
        <div class="match-card winner-card">
            <div style="text-align: center; padding: 2rem;">
                <h2 style="color: #1E3C72; margin: 0;">🏆 TOURNAMENT CHAMPION 🏆</h2>
                <h1 style="color: #1E3C72; margin: 1rem 0; font-size: 2.5em;">{flag} {winner}</h1>
                <p style="color: #1E3C72; margin: 0;">African Nations League 2025 Winner</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_match_control():
    if st.session_state.role != 'admin':
        st.error("🔒 Admin access required")
        return
    
    st.title("⚽ Match Control Center")
    db = safe_get_database()
    if db is None:
        st.error("Database unavailable")
        return
    
    # Tournament management
    st.subheader("🎯 Tournament Management")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Start Tournament", use_container_width=True):
            initialize_tournament(db)
            st.rerun()
    with col2:
        if st.button("🔄 Reset Tournament", use_container_width=True):
            try:
                db.matches.delete_many({})
                db.tournaments.delete_many({})
                st.success("Tournament reset!")
                st.rerun()
            except Exception as e:
                st.error(f"Reset failed: {str(e)}")
    with col3:
        if st.button("⚡ Auto Simulate All", use_container_width=True):
            simulate_all_matches(db)
            st.rerun()
    
    # Match simulation
    st.subheader("🎮 Match Simulation")
    try:
        scheduled_matches = list(db.matches.find({"status": "scheduled"}))
    except Exception as e:
        st.error(f"Error loading matches: {str(e)}")
        return
    
    if scheduled_matches:
        for match in scheduled_matches:
            st.write(f"**{match['teamA_name']} vs {match['teamB_name']}** ({match.get('stage', 'unknown')})")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Play with Commentary", key=f"play_{match['_id']}"):
                    play_match_with_commentary(match)
            with col2:
                if st.button(f"Quick Simulate", key=f"quick_{match['_id']}"):
                    simulate_match_quick(match)
            st.markdown("---")
    else:
        st.info("No scheduled matches available")

def play_match_with_commentary(match):
    try:
        db = safe_get_database()
        if db is None:
            st.error("Database unavailable")
            return
            
        score_a, score_b, goal_scorers, commentary = simulate_match_with_commentary(
            db, match["_id"], match['teamA_name'], match['teamB_name']
        )
        
        # Show match summary
        st.success(f"**Final: {match['teamA_name']} {score_a}-{score_b} {match['teamB_name']}**")
        
        with st.expander("Match Commentary"):
            for comment in commentary:
                st.write(f"• {comment}")
        
        if goal_scorers:
            st.write("**Goal Scorers:**")
            for goal in goal_scorers:
                st.write(f"- {goal['player']} ({goal['minute']}') - {goal['team']}")
        
        # Advance tournament
        advance_tournament(db, match)
        st.rerun()
        
    except Exception as e:
        st.error(f"Match simulation error: {str(e)}")
        simulate_match_quick(match)

def simulate_match_quick(match):
    db = safe_get_database()
    if db is None:
        st.error("Database unavailable")
        return
        
    score_a = random.randint(0, 3)
    score_b = random.randint(0, 3)
    
    goal_scorers = []
    for i in range(score_a):
        goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": random.randint(1, 90), "team": match['teamA_name']})
    for i in range(score_b):
        goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": random.randint(1, 90), "team": match['teamB_name']})
    
    try:
        db.matches.update_one(
            {"_id": match["_id"]},
            {"$set": {
                "status": "completed",
                "scoreA": score_a,
                "scoreB": score_b,
                "goal_scorers": goal_scorers,
                "method": "simulated"
            }}
        )
        
        advance_tournament(db, match)
        st.success(f"Match simulated: {match['teamA_name']} {score_a}-{score_b} {match['teamB_name']}")
        st.rerun()
    except Exception as e:
        st.error(f"Simulation failed: {str(e)}")

def initialize_tournament(db):
    try:
        teams = list(db.federations.find({}).limit(8))
        if len(teams) < 8:
            st.error(f"Need 8 teams. Currently: {len(teams)}")
            return
        
        random.shuffle(teams)
        db.matches.delete_many({})
        
        # Create quarter-finals
        for i in range(0, 8, 2):
            match_data = {
                "teamA_name": teams[i]["country"],
                "teamB_name": teams[i+1]["country"],
                "stage": "quarterfinal",
                "status": "scheduled",
                "scoreA": 0, "scoreB": 0,
                "created_at": datetime.now()
            }
            db.matches.insert_one(match_data)
        
        db.tournaments.update_one({}, {"$set": {"status": "active", "current_stage": "quarterfinal"}}, upsert=True)
        st.success("🎊 Tournament started! Quarter-finals created.")
    except Exception as e:
        st.error(f"Tournament start failed: {str(e)}")

def advance_tournament(db, completed_match):
    try:
        stage = completed_match.get('stage')
        all_matches = list(db.matches.find({"stage": stage}))
        
        if all(m.get('status') == 'completed' for m in all_matches):
            if stage == "quarterfinal":
                create_semifinals(db)
            elif stage == "semifinal":
                create_final(db)
    except Exception as e:
        st.error(f"Tournament advancement failed: {str(e)}")

def create_semifinals(db):
    try:
        quarters = list(db.matches.find({"stage": "quarterfinal", "status": "completed"}))
        winners = []
        
        for match in quarters:
            winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
            winners.append(winner)
        
        for i in range(0, 4, 2):
            match_data = {
                "teamA_name": winners[i],
                "teamB_name": winners[i+1],
                "stage": "semifinal",
                "status": "scheduled",
                "scoreA": 0, "scoreB": 0,
                "created_at": datetime.now()
            }
            db.matches.insert_one(match_data)
        
        db.tournaments.update_one({}, {"$set": {"current_stage": "semifinal"}})
        st.success("Semi-finals created!")
    except Exception as e:
        st.error(f"Semi-final creation failed: {str(e)}")

def create_final(db):
    try:
        semis = list(db.matches.find({"stage": "semifinal", "status": "completed"}))
        winners = []
        
        for match in semis:
            winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
            winners.append(winner)
        
        match_data = {
            "teamA_name": winners[0],
            "teamB_name": winners[1],
            "stage": "final",
            "status": "scheduled",
            "scoreA": 0, "scoreB": 0,
            "created_at": datetime.now()
        }
        db.matches.insert_one(match_data)
        db.tournaments.update_one({}, {"$set": {"current_stage": "final"}})
        st.success("Final match created!")
    except Exception as e:
        st.error(f"Final creation failed: {str(e)}")

def simulate_all_matches(db):
    try:
        scheduled = list(db.matches.find({"status": "scheduled"}))
        for match in scheduled:
            simulate_match_quick(match)
        st.success("All matches simulated!")
    except Exception as e:
        st.error(f"Simulation failed: {str(e)}")

def show_my_team():
    if st.session_state.role != 'federation':
        st.info("Federation access required")
        return
    
    db = safe_get_database()
    if db is None:
        st.error("Database unavailable")
        return
        
    try:
        user_team = db.federations.find_one({"representative_email": st.session_state.user['email']})
    except Exception as e:
        st.error(f"Error loading team data: {str(e)}")
        return
    
    if user_team:
        st.title(f"👥 {user_team['country']} National Team")
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Manager", user_team.get('manager', 'Unknown'))
        with col2: st.metric("Team Rating", user_team.get('rating', 75))
        with col3: st.metric("Squad Size", f"{len(user_team.get('players', []))}/23")
        
        # Show squad
        st.subheader("Team Squad")
        for pos in ["GK", "DF", "MD", "AT"]:
            players = [p for p in user_team.get('players', []) if p['naturalPosition'] == pos]
            if players:
                with st.expander(f"{pos} - {len(players)} players"):
                    for player in players:
                        captain = " ⭐" if player.get('isCaptain') else ""
                        rating = player['ratings'][player['naturalPosition']]
                        st.write(f"**{player['name']}** - Rating: {rating}{captain}")
    else:
        st.error("No team found")

def show_analytics():
    if st.session_state.role != 'admin':
        st.error("Admin access required")
        return
    show_statistics_content(True)

def show_statistics():
    show_statistics_content(False)

def show_statistics_content(is_admin):
    st.title("📊 Tournament Statistics")
    db = safe_get_database()
    
    if db is None:
        st.error("Database unavailable")
        return
    
    try:
        # Team standings
        st.subheader("🏆 Team Standings")
        teams = list(db.federations.find({}).sort("rating", -1))
        for i, team in enumerate(teams):
            flag = COUNTRY_FLAGS.get(team['country'], "🏴")
            if i == 0: st.write(f"🥇 **{flag} {team['country']}** - Rating: {team.get('rating', 75)}")
            elif i == 1: st.write(f"🥈 **{flag} {team['country']}** - Rating: {team.get('rating', 75)}")
            elif i == 2: st.write(f"🥉 **{flag} {team['country']}** - Rating: {team.get('rating', 75)}")
            else: st.write(f"**{flag} {team['country']}** - Rating: {team.get('rating', 75)}")
        
        # Top scorers
        st.subheader("🥅 Top Scorers")
        matches = list(db.matches.find({"status": "completed"}))
        goal_scorers = []
        for match in matches:
            goal_scorers.extend(match.get('goal_scorers', []))
        
        if goal_scorers:
            scorer_counts = {}
            for goal in goal_scorers:
                scorer_counts[goal['player']] = scorer_counts.get(goal['player'], 0) + 1
            
            for player, goals in sorted(scorer_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                st.write(f"**{player}** - {goals} goals")
        else:
            st.info("No goals scored yet")
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

if __name__ == "__main__":
    main()
