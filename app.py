import streamlit as st
import time
import random
from datetime import datetime
from frontend.utils.auth import init_session_state, login_user, logout_user, register_user
from frontend.utils.database import get_database, initialize_database, is_database_available, get_team_count
from frontend.utils.match_simulator import simulate_match_with_commentary

# Initialize
init_session_state()
st.set_page_config(
    page_title="African Nations League", 
    layout="wide", 
    page_icon="⚽",
    initial_sidebar_state="expanded"
)

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

# Professional CSS (hides Streamlit branding)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        border: 4px solid #FFD700;
    }
    .team-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem;
        border: 2px solid #1E3C72;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .team-card:hover {
        transform: translateY(-5px);
    }
    .match-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #1E3C72;
    }
    .leaderboard-item {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.3rem 0;
        border-left: 4px solid #FFD700;
    }
    .progress-bar {
        background: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 20px;
        margin: 0.5rem 0;
    }
    .progress-fill {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        height: 100%;
        transition: width 0.5s;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    initialize_database()
    
    if not st.session_state.get('user'):
        show_login_page()
    else:
        show_app()

def show_login_page():
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color: #FFD700; font-size: 3em;">🏆 AFRICAN NATIONS LEAGUE</h1>
        <p style="margin:0; font-size: 1.5em;">Road to Glory 2025</p>
        <p style="margin:0; font-size: 1em;">INF4001N: 2025 Entrance Exam Brief for 2026</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Admin Login", "🇺🇳 Federation Sign Up", "👤 Visitor Access"])
    
    with tab1:
        st.subheader("Administrator Login")
        with st.form("admin_login"):
            email = st.text_input("Email", placeholder="admin@africanleague.com")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("🚀 Login as Admin", use_container_width=True):
                if login_user(email, password):
                    st.success("Welcome Admin!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        show_federation_registration()
    
    with tab3:
        st.subheader("Visitor Access")
        st.info("Explore tournament matches, standings, and statistics")
        if st.button("👀 Enter as Visitor", use_container_width=True, type="primary"):
            st.session_state.user = {"email": "visitor", "role": "visitor"}
            st.session_state.role = "visitor"
            st.rerun()

def show_federation_registration():
    st.subheader("Federation Registration")
    db = get_database()
    
    team_count = db.federations.count_documents({}) if db else 0
    st.info(f"📊 Teams registered: {team_count}/8")
    
    if team_count >= 8:
        st.warning("🎯 Tournament full! New registrations will be waitlisted.")
    
    with st.form("register_team"):
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("Select Country", AFRICAN_COUNTRIES)
            manager = st.text_input("Manager Name")
        with col2:
            rep_name = st.text_input("Representative Name")
            rep_email = st.text_input("Email")
            password = st.text_input("Password", type="password")
        
        if st.form_submit_button("🚀 Register Federation", use_container_width=True):
            if register_federation(country, manager, rep_name, rep_email, password):
                st.success("Federation registered successfully!")
                if login_user(rep_email, password):
                    st.rerun()

def register_federation(country, manager, rep_name, rep_email, password):
    try:
        db = get_database()
        if db.federations.find_one({"country": country}):
            st.error("Country already registered")
            return False
        
        if not register_user(rep_email, password, "federation", country):
            st.error("Registration failed")
            return False
        
        # Auto-generate squad
        squad = []
        positions = {"GK": 3, "DF": 7, "MD": 8, "AT": 5}
        for pos, count in positions.items():
            for i in range(count):
                player = {
                    "name": f"Player {random.randint(1, 100)}",
                    "naturalPosition": pos,
                    "ratings": {p: random.randint(50, 100) if p == pos else random.randint(0, 50) for p in ["GK", "DF", "MD", "AT"]},
                    "isCaptain": False
                }
                squad.append(player)
        
        if squad:
            squad[0]["isCaptain"] = True
        
        team_rating = sum(p["ratings"][p["naturalPosition"]] for p in squad) / len(squad)
        
        team_data = {
            "country": country,
            "manager": manager,
            "representative_name": rep_name,
            "representative_email": rep_email,
            "rating": round(team_rating, 2),
            "players": squad,
            "registered_at": datetime.now()
        }
        
        db.federations.insert_one(team_data)
        
        if db.federations.count_documents({}) >= 8:
            initialize_tournament(db)
            st.balloons()
            st.success("🎊 Tournament started with 8 teams!")
        
        return True
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def show_app():
    # Sidebar navigation
    with st.sidebar:
        user_role = st.session_state.role.upper()
        st.markdown(f"### 👋 Welcome, {st.session_state.user['email']}")
        st.markdown(f"**Role:** {user_role}")
        st.markdown("---")
        
        # Role-based navigation
        if st.session_state.role == "admin":
            pages = ["🏠 Home Dashboard", "🏆 Tournament Bracket", "⚽ Match Control", "📊 Analytics"]
        elif st.session_state.role == "federation":
            pages = ["🏠 Home Dashboard", "🏆 Tournament Bracket", "👥 My Team", "📊 Statistics"]
        else:
            pages = ["🏠 Home Dashboard", "🏆 Tournament Bracket", "📊 Statistics"]
        
        for page in pages:
            if st.button(page, use_container_width=True, type="primary" if st.session_state.get('current_page') == page else "secondary"):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Show current page
    current_page = st.session_state.get('current_page', '🏠 Home Dashboard')
    
    if current_page == "🏠 Home Dashboard":
        show_home_dashboard()
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

def show_home_dashboard():
    """Enhanced home page with teams, progress, match history, and leaderboard"""
    db = get_database()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color: #FFD700; font-size: 2.8em;">🏆 AFRICAN NATIONS LEAGUE</h1>
        <p style="margin:0; font-size: 1.3em; font-weight: bold;">Tournament Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data
    teams = list(db.federations.find({}).sort("rating", -1))
    matches = list(db.matches.find({}))
    completed_matches = [m for m in matches if m.get('status') == 'completed']
    tournament = db.tournaments.find_one({}) or {}
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("Total Teams", len(teams))
    with col2: 
        st.metric("Matches Played", len(completed_matches))
    with col3: 
        st.metric("Tournament Status", "Active" if tournament.get('status') == 'active' else "Ready")
    with col4: 
        st.metric("Current Stage", tournament.get('current_stage', 'Not Started').replace('_', ' ').title())
    
    st.markdown("---")
    
    # Two-column layout for main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Registered Teams with Flags
        st.subheader("🇺🇳 Registered Teams")
        if teams:
            # Display teams in a grid
            cols = st.columns(4)
            for i, team in enumerate(teams):
                with cols[i % 4]:
                    flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                    rating = team.get('rating', 75)
                    st.markdown(f"""
                    <div class="team-card">
                        <h3 style="margin:0; font-size: 2em;">{flag}</h3>
                        <h4 style="margin:5px 0; color: #1E3C72;">{team['country']}</h4>
                        <p style="margin:0; color: #666; font-size: 0.9em;">Rating: {rating}</p>
                        <p style="margin:0; color: #888; font-size: 0.8em;">{team.get('manager', 'Unknown')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No teams registered yet")
        
        # Match History
        st.markdown("---")
        st.subheader("📅 Recent Matches")
        if completed_matches:
            recent_matches = completed_matches[-5:]  # Last 5 matches
            for match in reversed(recent_matches):
                flag_a = COUNTRY_FLAGS.get(match['teamA_name'], "🏴")
                flag_b = COUNTRY_FLAGS.get(match['teamB_name'], "🏴")
                st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{flag_a} {match['teamA_name']}</strong></span>
                        <span><strong>{match['scoreA']} - {match['scoreB']}</strong></span>
                        <span><strong>{match['teamB_name']} {flag_b}</strong></span>
                    </div>
                    <div style="text-align: center; color: #666; font-size: 0.8em;">
                        {match.get('stage', '').title()} • {match.get('method', 'simulated').title()}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No matches played yet")
    
    with col2:
        # Tournament Progress
        st.subheader("📊 Tournament Progress")
        total_matches = len(matches)
        completed_count = len(completed_matches)
        
        if total_matches > 0:
            progress = (completed_count / total_matches) * 100
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <div style="text-align: center; font-weight: bold;">
                {completed_count}/{total_matches} matches ({progress:.0f}%)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Tournament not started")
        
        # Current Stage Info
        current_stage = tournament.get('current_stage', 'Not Started')
        stage_info = {
            'quarterfinal': '🎯 Quarter Finals - 4 matches',
            'semifinal': '🔥 Semi Finals - 2 matches', 
            'final': '🏆 Grand Final - 1 match',
            'Not Started': '⏳ Tournament ready to start'
        }
        st.info(f"**Current Stage:** {stage_info.get(current_stage, current_stage)}")
        
        # Leaderboard
        st.markdown("---")
        st.subheader("🏅 Team Leaderboard")
        if teams:
            for i, team in enumerate(teams[:5]):  # Top 5 teams
                flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                st.markdown(f"""
                <div class="leaderboard-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{medal} {flag} {team['country']}</strong></span>
                        <span style="color: #1E3C72; font-weight: bold;">{team.get('rating', 75)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No teams yet")
        
        # Quick Stats
        st.markdown("---")
        st.subheader("⚡ Quick Stats")
        total_goals = sum(len(match.get('goal_scorers', [])) for match in completed_matches)
        st.metric("Total Goals", total_goals)
        
        if completed_matches:
            avg_goals = total_goals / len(completed_matches)
            st.metric("Avg Goals/Match", f"{avg_goals:.1f}")
    
    # Admin Quick Actions
    if st.session_state.role == 'admin' and len(teams) >= 8:
        st.markdown("---")
        st.subheader("⚡ Admin Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Start Tournament", use_container_width=True):
                initialize_tournament(db)
                st.rerun()
        with col2:
            if st.button("⚡ Simulate All", use_container_width=True):
                simulate_all_matches(db)
                st.rerun()
        with col3:
            if st.button("📊 View Full Bracket", use_container_width=True):
                st.session_state.current_page = "🏆 Tournament Bracket"
                st.rerun()

# ... (keep all your existing functions for tournament bracket, match control, etc. from previous versions)

def initialize_tournament(db):
    """Initialize tournament bracket with 8 teams"""
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

def simulate_match_quick(match):
    db = get_database()
    score_a = random.randint(0, 3)
    score_b = random.randint(0, 3)
    
    goal_scorers = []
    for i in range(score_a):
        goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": random.randint(1, 90), "team": match['teamA_name']})
    for i in range(score_b):
        goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": random.randint(1, 90), "team": match['teamB_name']})
    
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

def advance_tournament(db, completed_match):
    stage = completed_match.get('stage')
    all_matches = list(db.matches.find({"stage": stage}))
    
    if all(m.get('status') == 'completed' for m in all_matches):
        if stage == "quarterfinal":
            create_semifinals(db)
        elif stage == "semifinal":
            create_final(db)

def create_semifinals(db):
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

def create_final(db):
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

def simulate_all_matches(db):
    scheduled = list(db.matches.find({"status": "scheduled"}))
    for match in scheduled:
        simulate_match_quick(match)
    st.success("All matches simulated!")

# ... (include your existing show_tournament_bracket, show_match_control, show_my_team, show_analytics, show_statistics functions here)

def show_tournament_bracket():
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color: #FFD700; font-size: 2.5em;">🏆 AFRICAN NATIONS LEAGUE 2025</h1>
        <p style="margin:0; font-size: 1.3em; font-weight: bold;">ROAD TO THE FINAL</p>
    </div>
    """, unsafe_allow_html=True)
    
    db = get_database()
    show_full_tournament_bracket(db)

def show_full_tournament_bracket(db):
    matches = list(db.matches.find({}))
    
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
    
    st.markdown(f"<div style='background: #1E3C72; color: white; padding: 1rem; border-radius: 8px; text-align: center; margin: 1rem 0;'><h3>{title}</h3></div>", unsafe_allow_html=True)
    
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

def show_champion(matches):
    final_matches = [m for m in matches if m.get('stage') == 'final' and m.get('status') == 'completed']
    
    if final_matches:
        final = final_matches[0]
        winner = final['teamA_name'] if final['scoreA'] > final['scoreB'] else final['teamB_name']
        flag = COUNTRY_FLAGS.get(winner, "🏆")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFD700 0%, #FFEC8B 100%); 
                    padding: 2rem; border-radius: 15px; text-align: center; 
                    border: 3px solid #1E3C72; margin-top: 2rem;">
            <h2 style="color: #1E3C72; margin: 0;">🏆 TOURNAMENT CHAMPION 🏆</h2>
            <h1 style="color: #1E3C72; margin: 1rem 0; font-size: 2.5em;">{flag} {winner}</h1>
            <p style="color: #1E3C72; margin: 0;">African Nations League 2025 Winner</p>
        </div>
        """, unsafe_allow_html=True)

# Add other existing functions (show_match_control, show_my_team, show_analytics, show_statistics) here...

if __name__ == "__main__":
    main()
