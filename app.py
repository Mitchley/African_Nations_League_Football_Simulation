import streamlit as st
import time
import random
from datetime import datetime

# Import your existing modules
try:
    from frontend.utils.auth import init_session_state, login_user, logout_user, register_user
    from frontend.utils.database import get_database, initialize_database, is_database_available, get_team_count
    from frontend.utils.match_simulator import simulate_match_with_commentary
except ImportError as e:
    st.error(f"Import error: {e}")
    # Create dummy functions for testing
    def init_session_state(): pass
    def login_user(*args): return False
    def logout_user(): pass
    def register_user(*args): return False
    def get_database(): return None
    def initialize_database(): pass
    def is_database_available(): return False
    def get_team_count(): return 0
    def simulate_match_with_commentary(*args): return (0, 0, [], [])

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

# Enhanced CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        border: 4px solid #FFD700;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        border: 2px solid #e0e0e0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
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
    .tournament-bracket {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #dee2e6;
    }
    .stage-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        font-weight: bold;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
    }
    .login-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    try:
        initialize_database()
        
        if not st.session_state.get('user'):
            show_login_page()
        else:
            # Set default page to dashboard if not set
            if 'current_page' not in st.session_state:
                st.session_state.current_page = "🏠 Home Dashboard"
            show_app()
    except Exception as e:
        st.error(f"Application error: {str(e)}")

def show_login_page():
    """Show only login/signup options without tournament details"""
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color: #FFD700; font-size: 3em;">🏆 AFRICAN NATIONS LEAGUE</h1>
        <p style="margin:0; font-size: 1.5em; font-weight: bold;">Road to Glory 2025</p>
        <p style="margin:0; font-size: 1em;">The Ultimate African Football Tournament Experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights - SIMPLIFIED for login page only
    st.subheader("🎯 What You Can Do")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>⚽ Realistic Match Simulation</h3>
            <p>Watch AI-powered matches with dynamic commentary and realistic outcomes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🌍 Represent Your Nation</h3>
            <p>Register as a federation and lead your country to continental glory</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Live Tournament Tracking</h3>
            <p>Follow the complete bracket from quarter-finals to championship</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # AUTHENTICATION SECTION - Focus only on login/signup
    st.subheader("🔐 Get Started - Choose Your Role")
    
    tab1, tab2, tab3 = st.tabs(["👑 Admin Login", "🇺🇳 Federation Sign Up", "👀 Visitor Access"])
    
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
            st.session_state.current_page = "🏠 Home Dashboard"  # Set default page
            st.rerun()

def show_federation_registration():
    """Show federation registration form"""
    db = get_database()
    if db is None:
        st.error("❌ Cannot access database. Please check your MongoDB connection.")
        return
    
    team_count = get_team_count()
    
    st.info(f"📊 Teams registered: {team_count}/8")
    
    # Progress bar
    progress = min(team_count / 8 * 100, 100)
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress}%"></div>
    </div>
    """, unsafe_allow_html=True)
    
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
                    st.session_state.current_page = "🏠 Home Dashboard"  # Set default page
                    st.rerun()

def register_federation(country, manager, rep_name, rep_email, password):
    try:
        db = get_database()
        if db is None:
            st.error("Database unavailable")
            return False
            
        existing_team = db.federations.find_one({"country": country})
        if existing_team:
            st.error("Country already registered")
            return False
        
        if not register_user(rep_email, password, "federation", country):
            st.error("Registration failed")
            return False
        
        # Auto-generate squad with realistic African names
        squad = generate_realistic_squad()
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
        
        if get_team_count() >= 8:
            initialize_tournament(db)
            st.balloons()
            st.success("🎊 Tournament started with 8 teams!")
        
        return True
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def generate_realistic_squad():
    """Generate a squad with realistic African player names"""
    first_names = ["Mohamed", "Ibrahim", "Ahmed", "Youssef", "Samuel", "David", "Kwame", "Kofi", 
                  "Chukwu", "Adebayo", "Musa", "Said", "Rashid", "Tendai", "Blessing", "Prince",
                  "Emmanuel", "Daniel", "Joseph", "Victor", "Alex", "Boubacar", "Moussa", "Abdul"]
    
    last_names = ["Traore", "Diallo", "Keita", "Camara", "Sow", "Diop", "Ndiaye", "Gueye",
                 "Mensah", "Appiah", "Owusu", "Adeyemi", "Okafor", "Okoro", "Mohammed", "Ali",
                 "Hussein", "Juma", "Kamau", "Nkosi", "Zulu", "Van Wyk", "Silva", "Santos"]
    
    squad = []
    positions = {"GK": 3, "DF": 7, "MD": 8, "AT": 5}
    
    for pos, count in positions.items():
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            player_name = f"{first_name} {last_name}"
            
            player = {
                "name": player_name,
                "naturalPosition": pos,
                "ratings": {p: random.randint(50, 100) if p == pos else random.randint(0, 50) for p in ["GK", "DF", "MD", "AT"]},
                "isCaptain": False
            }
            squad.append(player)
    
    if squad:
        squad[0]["isCaptain"] = True
    
    return squad

def show_app():
    with st.sidebar:
        user_role = st.session_state.role.upper()
        st.markdown(f"### 👋 Welcome, {st.session_state.user['email']}")
        st.markdown(f"**Role:** {user_role}")
        st.markdown("---")
        
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
    
    # Always show the current page content - no need to click dashboard first
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
    """Show the main dashboard with all tournament details AFTER login"""
    db = get_database()
    
    if db is None:
        st.error("❌ Database connection failed")
        return
    
    # Welcome header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color: #FFD700; font-size: 2.8em;">🏆 WELCOME TO AFRICAN NATIONS LEAGUE 2024</h1>
        <p style="margin:0; font-size: 1.3em; font-weight: bold;">Tournament Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # TOURNAMENT OVERVIEW - Now shown only after login
    st.subheader("📊 Tournament Overview")
    
    teams = get_federations()
    matches = get_matches()
    completed_matches = [m for m in matches if m.get('status') == 'completed']
    tournament_data = get_tournaments()
    tournament = tournament_data[0] if tournament_data else {}
    
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
    
    # Show registered teams
    if teams:
        st.subheader("🇺🇳 Currently Registered Teams")
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
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("---")
        st.subheader("📅 Recent Matches")
        if completed_matches:
            recent_matches = completed_matches[-5:]
            for match in reversed(recent_matches):
                flag_a = COUNTRY_FLAGS.get(match.get('teamA_name', 'Team A'), "🏴")
                flag_b = COUNTRY_FLAGS.get(match.get('teamB_name', 'Team B'), "🏴")
                st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{flag_a} {match.get('teamA_name', 'Team A')}</strong></span>
                        <span><strong>{match.get('scoreA', 0)} - {match.get('scoreB', 0)}</strong></span>
                        <span><strong>{match.get('teamB_name', 'Team B')} {flag_b}</strong></span>
                    </div>
                    <div style="text-align: center; color: #666; font-size: 0.8em;">
                        {match.get('stage', '').title()} • {match.get('method', 'simulated').title()}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No matches played yet")
    
    with col2:
        st.subheader("📈 Tournament Progress")
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
        
        current_stage = tournament.get('current_stage', 'Not Started')
        stage_info = {
            'quarterfinal': '🎯 Quarter Finals - 4 matches',
            'semifinal': '🔥 Semi Finals - 2 matches', 
            'final': '🏆 Grand Final - 1 match',
            'Not Started': '⏳ Tournament ready to start'
        }
        st.info(f"**Current Stage:** {stage_info.get(current_stage, current_stage)}")
        
        st.markdown("---")
        st.subheader("🏅 Team Leaderboard")
        if teams:
            for i, team in enumerate(teams[:5]):  # Show top 5 only
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
    
    if st.session_state.role == 'admin' and len(teams) >= 8:
        st.markdown("---")
        st.subheader("⚡ Admin Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Start Tournament", use_container_width=True):
                db = get_database()
                if db is not None:
                    initialize_tournament(db)
                st.rerun()
        with col2:
            if st.button("⚡ Simulate All", use_container_width=True):
                db = get_database()
                if db is not None:
                    simulate_all_matches(db)
                st.rerun()
        with col3:
            if st.button("📊 View Full Bracket", use_container_width=True):
                st.session_state.current_page = "🏆 Tournament Bracket"
                st.rerun()

def show_tournament_bracket():
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color: #FFD700; font-size: 2.5em;">🏆 AFRICAN NATIONS LEAGUE 2025</h1>
        <p style="margin:0; font-size: 1.3em; font-weight: bold;">ROAD TO THE FINAL</p>
    </div>
    """, unsafe_allow_html=True)
    
    db = get_database()
    if db is None:
        st.error("❌ Database unavailable")
        return
    
    show_enhanced_tournament_bracket(db)

def show_enhanced_tournament_bracket(db):
    matches = get_matches()
    tournament_data = get_tournaments()
    tournament = tournament_data[0] if tournament_data else {}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tournament Stage", tournament.get('current_stage', 'Not Started').replace('_', ' ').title())
    with col2:
        total_matches = len(matches)
        completed_matches = len([m for m in matches if m.get('status') == 'completed'])
        st.metric("Matches Completed", f"{completed_matches}/{total_matches}")
    with col3:
        if tournament.get('status') == 'active':
            st.metric("Status", "🏃‍♂️ LIVE", "Active")
        else:
            st.metric("Status", "⏳ READY", "Waiting")
    
    st.markdown("---")
    
    if not matches:
        st.info("🎯 Tournament not started. Admin can start when 8 teams are registered.")
        
        teams = get_federations()
        if len(teams) >= 8:
            st.subheader("🎊 Ready to Start! Here's how the bracket would look:")
            random.shuffle(teams)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.markdown('<div class="stage-header">QUARTER FINALS</div>', unsafe_allow_html=True)
                for i in range(0, 8, 2):
                    flag1 = COUNTRY_FLAGS.get(teams[i]['country'], "🏴")
                    flag2 = COUNTRY_FLAGS.get(teams[i+1]['country'], "🏴")
                    st.markdown(f"""
                    <div class="tournament-bracket">
                        <div style="text-align: center; font-weight: bold; margin-bottom: 10px;">
                            Match {i//2 + 1}
                        </div>
                        <div style="text-align: center; font-size: 1.1em;">
                            {flag1} {teams[i]['country']}
                        </div>
                        <div style="text-align: center; margin: 8px 0; font-weight: bold;">VS</div>
                        <div style="text-align: center; font-size: 1.1em;">
                            {flag2} {teams[i+1]['country']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="stage-header">SEMI FINALS</div>', unsafe_allow_html=True)
                st.info("Winners from Quarter-Finals will advance here")
                for i in range(2):
                    st.markdown(f"""
                    <div class="tournament-bracket">
                        <div style="text-align: center; color: #666; padding: 2rem;">
                            Semi-Final {i+1}<br>
                            <small>Waiting for Quarter-Finals</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="stage-header">GRAND FINAL</div>', unsafe_allow_html=True)
                st.markdown("""
                <div class="tournament-bracket">
                    <div style="text-align: center; color: #666; padding: 2rem;">
                        🏆 Championship Match<br>
                        <small>Winners from Semi-Finals</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        return
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown('<div class="stage-header">QUARTER FINALS</div>', unsafe_allow_html=True)
        quarter_matches = [m for m in matches if m.get('stage') == 'quarterfinal']
        
        if not quarter_matches:
            st.info("⏳ Quarter-finals not created")
        else:
            for i, match in enumerate(quarter_matches):
                display_enhanced_match_card(match, f"QF {i+1}", "Semi-Finals")
    
    with col2:
        st.markdown('<div class="stage-header">SEMI FINALS</div>', unsafe_allow_html=True)
        semi_matches = [m for m in matches if m.get('stage') == 'semifinal']
        
        if not semi_matches:
            completed_quarters = [m for m in quarter_matches if m.get('status') == 'completed']
            if len(completed_quarters) == 4:
                winners = []
                for match in completed_quarters:
                    winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
                    winners.append(winner)
                
                for i in range(0, 4, 2):
                    flag1 = COUNTRY_FLAGS.get(winners[i], "🏴")
                    flag2 = COUNTRY_FLAGS.get(winners[i+1], "🏴")
                    st.markdown(f"""
                    <div class="tournament-bracket" style="background: #e3f2fd;">
                        <div style="text-align: center; font-weight: bold;">
                            Semi-Final {i//2 + 1}
                        </div>
                        <div style="text-align: center; margin: 10px 0;">
                            {flag1} {winners[i]}
                        </div>
                        <div style="text-align: center; margin: 8px 0; font-weight: bold;">VS</div>
                        <div style="text-align: center; margin: 10px 0;">
                            {flag2} {winners[i+1]}
                        </div>
                        <div style="text-align: center; color: #1976d2; font-size: 0.9em;">
                            Ready to be created
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("⏳ Waiting for quarter-final results...")
        else:
            for i, match in enumerate(semi_matches):
                display_enhanced_match_card(match, f"SF {i+1}", "Final")
    
    with col3:
        st.markdown('<div class="stage-header">GRAND FINAL</div>', unsafe_allow_html=True)
        final_matches = [m for m in matches if m.get('stage') == 'final']
        
        if not final_matches:
            completed_semis = [m for m in semi_matches if m.get('status') == 'completed']
            if len(completed_semis) == 2:
                winners = []
                for match in completed_semis:
                    winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
                    winners.append(winner)
                
                flag1 = COUNTRY_FLAGS.get(winners[0], "🏴")
                flag2 = COUNTRY_FLAGS.get(winners[1], "🏴")
                st.markdown(f"""
                <div class="tournament-bracket" style="background: #fff3cd; border: 2px solid #FFD700;">
                    <div style="text-align: center; font-weight: bold; color: #856404;">
                        🏆 CHAMPIONSHIP
                    </div>
                    <div style="text-align: center; margin: 15px 0; font-size: 1.1em;">
                        {flag1} {winners[0]}
                    </div>
                    <div style="text-align: center; margin: 10px 0; font-weight: bold; font-size: 1.2em;">
                        VS
                    </div>
                    <div style="text-align: center; margin: 15px 0; font-size: 1.1em;">
                        {flag2} {winners[1]}
                    </div>
                    <div style="text-align: center; color: #856404; font-size: 0.9em;">
                        Ready to be created
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("⏳ Waiting for semi-final results...")
        else:
            final_match = final_matches[0]
            if final_match.get('status') == 'completed':
                winner = final_match['teamA_name'] if final_match['scoreA'] > final_match['scoreB'] else final_match['teamB_name']
                winner_flag = COUNTRY_FLAGS.get(winner, "🏆")
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #FFD700 0%, #FFEC8B 100%); 
                            padding: 2rem; border-radius: 15px; text-align: center; 
                            border: 3px solid #1E3C72; margin-top: 1rem;">
                    <h2 style="color: #1E3C72; margin: 0;">🏆 TOURNAMENT CHAMPION 🏆</h2>
                    <h1 style="color: #1E3C72; margin: 1rem 0; font-size: 2.5em;">{winner_flag} {winner}</h1>
                    <p style="color: #1E3C72; margin: 0; font-size: 1.1em;">African Nations League 2025 Winner</p>
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.5); border-radius: 10px;">
                        <strong>Final Score: {final_match['teamA_name']} {final_match['scoreA']} - {final_match['scoreB']} {final_match['teamB_name']}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                display_enhanced_match_card(final_match, "FINAL", "CHAMPION")

def display_enhanced_match_card(match, match_label, next_round):
    flag_a = COUNTRY_FLAGS.get(match.get('teamA_name', 'Team A'), "🏴")
    flag_b = COUNTRY_FLAGS.get(match.get('teamB_name', 'Team B'), "🏴")
    
    if match.get('status') == 'completed':
        winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
        winner_flag = flag_a if match['scoreA'] > match['scoreB'] else flag_b
        
        st.markdown(f"""
        <div class="tournament-bracket" style="background: #d4edda;">
            <div style="text-align: center; font-weight: bold; color: #155724;">
                {match_label}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;">
                <span>{flag_a} {match['teamA_name']}</span>
                <span style="font-weight: bold; font-size: 1.2em;">{match['scoreA']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;">
                <span>{flag_b} {match['teamB_name']}</span>
                <span style="font-weight: bold; font-size: 1.2em;">{match['scoreB']}</span>
            </div>
            <div style="text-align: center; margin-top: 10px; padding: 8px; background: #c3e6cb; border-radius: 5px;">
                <strong>➡️ Advances to {next_round}: {winner_flag} {winner}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="tournament-bracket">
            <div style="text-align: center; font-weight: bold; color: #1E3C72;">
                {match_label}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;">
                <span style="font-weight: bold;">{flag_a} {match['teamA_name']}</span>
                <span style="font-weight: bold;">VS</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;">
                <span style="font-weight: bold;">{flag_b} {match['teamB_name']}</span>
                <span style="font-size: 1.2em;">⏰</span>
            </div>
            <div style="text-align: center; margin-top: 10px; color: #666; font-size: 0.9em;">
                Winner advances to {next_round}
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_match_control():
    if st.session_state.role != 'admin':
        st.error("🔒 Admin access required")
        return
    
    st.title("⚽ Match Control Center")
    db = get_database()
    if db is None:
        st.error("Database unavailable")
        return
    
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
    
    st.subheader("🎮 Match Simulation")
    scheduled_matches = get_matches({"status": "scheduled"})
    
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
        db = get_database()
        if db is None:
            st.error("Database unavailable")
            return
            
        # Get team data for realistic names
        team_a = db.federations.find_one({"country": match['teamA_name']})
        team_b = db.federations.find_one({"country": match['teamB_name']})
        
        score_a, score_b, goal_scorers, commentary = simulate_match_with_commentary(
            db, match["_id"], match['teamA_name'], match['teamB_name']
        )
        
        # Enhance goal_scorers with realistic names if available
        enhanced_goal_scorers = []
        for goal in goal_scorers:
            enhanced_goal = goal.copy()
            if goal['team'] == match['teamA_name'] and team_a and 'players' in team_a:
                # Replace generic name with actual player name
                player = random.choice(team_a['players'])
                enhanced_goal['player'] = player['name']
                assister = random.choice(team_a['players'])
                enhanced_goal['assist'] = f"Assist: {assister['name']}" if player['name'] != assister['name'] else "Solo goal"
            elif goal['team'] == match['teamB_name'] and team_b and 'players' in team_b:
                player = random.choice(team_b['players'])
                enhanced_goal['player'] = player['name']
                assister = random.choice(team_b['players'])
                enhanced_goal['assist'] = f"Assist: {assister['name']}" if player['name'] != assister['name'] else "Solo goal"
            else:
                enhanced_goal['assist'] = "Unassisted"
            
            enhanced_goal_scorers.append(enhanced_goal)
        
        st.success(f"**Final: {match['teamA_name']} {score_a}-{score_b} {match['teamB_name']}**")
        
        with st.expander("Match Commentary"):
            for comment in commentary:
                st.write(f"• {comment}")
        
        if enhanced_goal_scorers:
            st.write("**Goal Scorers:**")
            for goal in enhanced_goal_scorers:
                flag = COUNTRY_FLAGS.get(goal['team'], "🏴")
                st.write(f"- {goal['minute']}' - {flag} **{goal['player']}** ({goal['team']}) - {goal.get('assist', 'Unassisted')}")
        
        # Update match with enhanced goal data
        db.matches.update_one(
            {"_id": match["_id"]},
            {"$set": {
                "status": "completed",
                "scoreA": score_a,
                "scoreB": score_b,
                "goal_scorers": enhanced_goal_scorers,
                "method": "commentary"
            }}
        )
        
        advance_tournament(db, match)
        st.rerun()
        
    except Exception as e:
        st.error(f"Match simulation error: {str(e)}")
        simulate_match_quick(match)

def simulate_match_quick(match):
    db = get_database()
    if db is None:
        st.error("Database unavailable")
        return
        
    score_a = random.randint(0, 3)
    score_b = random.randint(0, 3)
    
    # Get team data for realistic player names
    team_a = db.federations.find_one({"country": match['teamA_name']})
    team_b = db.federations.find_one({"country": match['teamB_name']})
    
    goal_scorers = []
    
    # Generate goals for team A with realistic names
    for i in range(score_a):
        if team_a and 'players' in team_a:
            scorer = random.choice(team_a['players'])
            assister = random.choice(team_a['players'])
            goal_scorers.append({
                "player": scorer['name'],
                "minute": random.randint(1, 90),
                "team": match['teamA_name'],
                "assist": f"Assist: {assister['name']}" if scorer['name'] != assister['name'] else "Solo goal"
            })
        else:
            # Fallback if team data not available
            goal_scorers.append({
                "player": f"Player {random.randint(1, 23)}",
                "minute": random.randint(1, 90),
                "team": match['teamA_name'],
                "assist": f"Assist: Player {random.randint(1, 23)}"
            })
    
    # Generate goals for team B with realistic names
    for i in range(score_b):
        if team_b and 'players' in team_b:
            scorer = random.choice(team_b['players'])
            assister = random.choice(team_b['players'])
            goal_scorers.append({
                "player": scorer['name'],
                "minute": random.randint(1, 90),
                "team": match['teamB_name'],
                "assist": f"Assist: {assister['name']}" if scorer['name'] != assister['name'] else "Solo goal"
            })
        else:
            # Fallback if team data not available
            goal_scorers.append({
                "player": f"Player {random.randint(1, 23)}",
                "minute": random.randint(1, 90),
                "team": match['teamB_name'],
                "assist": f"Assist: Player {random.randint(1, 23)}"
            })
    
    # Sort goals by minute
    goal_scorers.sort(key=lambda x: x['minute'])
    
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
    
    db = get_database()
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
        with col1: 
            st.metric("Manager", user_team.get('manager', 'Unknown'))
        with col2: 
            st.metric("Team Rating", user_team.get('rating', 75))
        with col3: 
            st.metric("Squad Size", f"{len(user_team.get('players', []))}/23")
        
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
    db = get_database()
    
    if db is None:
        st.error("Database unavailable")
        return
    
    try:
        st.subheader("🏆 Team Standings")
        teams = list(db.federations.find({}).sort("rating", -1))
        
        if teams:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Full Team Rankings:**")
                for i, team in enumerate(teams):
                    flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                    
                    st.markdown(f"""
                    <div style="background: {'#fff3cd' if i < 3 else 'white'}; 
                                padding: 0.8rem; margin: 0.3rem 0; border-radius: 8px;
                                border-left: 4px solid {'#FFD700' if i < 3 else '#1E3C72'};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span><strong>{medal} {flag} {team['country']}</strong></span>
                            <span style="color: #1E3C72; font-weight: bold; font-size: 1.1em;">
                                {team.get('rating', 75)}
                            </span>
                        </div>
                        <div style="color: #666; font-size: 0.9em;">
                            Manager: {team.get('manager', 'Unknown')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            with col2:
                st.write("**Top Performers:**")
                if len(teams) >= 3:
                    for i in range(min(3, len(teams))):
                        team = teams[i]
                        flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                        st.metric(
                            f"{['🥇', '🥈', '🥉'][i]} {team['country']}",
                            f"Rating: {team.get('rating', 75)}"
                        )
        else:
            st.info("No teams registered yet")
        
        # IMPROVED TOP SCORERS SECTION
        st.subheader("🥅 Top Scorers")
        matches = list(db.matches.find({"status": "completed"}))
        goal_scorers = []
        
        # Enhanced goal tracking with player details
        for match in matches:
            for goal in match.get('goal_scorers', []):
                # Add match details and country to each goal
                goal_with_details = goal.copy()
                goal_with_details['match_id'] = match['_id']
                goal_with_details['stage'] = match.get('stage', 'Unknown')
                goal_with_details['country'] = goal['team']
                goal_scorers.append(goal_with_details)
        
        if goal_scorers:
            # Group goals by player and country
            scorer_counts = {}
            for goal in goal_scorers:
                key = (goal['player'], goal['country'])
                if key not in scorer_counts:
                    scorer_counts[key] = {
                        'goals': 0,
                        'matches': set(),
                        'details': []
                    }
                scorer_counts[key]['goals'] += 1
                scorer_counts[key]['matches'].add(goal['match_id'])
                # Find opponent for this goal
                opponent = None
                for m in matches:
                    if m['_id'] == goal['match_id']:
                        opponent = m['teamB_name'] if goal['team'] == m['teamA_name'] else m['teamA_name']
                        break
                
                scorer_counts[key]['details'].append({
                    'minute': goal['minute'],
                    'stage': goal['stage'],
                    'opponent': opponent or 'Unknown',
                    'score': f"{match['scoreA']}-{match['scoreB']}" if opponent else 'Unknown',
                    'assist': goal.get('assist', 'Unassisted')
                })
            
            # Display top scorers with enhanced information
            sorted_scorers = sorted(scorer_counts.items(), key=lambda x: x[1]['goals'], reverse=True)
            
            for i, ((player, country), data) in enumerate(sorted_scorers[:10]):
                flag = COUNTRY_FLAGS.get(country, "🏴")
                with st.expander(f"**{i+1}. {player}** - {flag} {country} - {data['goals']} goals ({len(data['matches'])} matches)", expanded=i < 3):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Goal Details:**")
                        for detail in sorted(data['details'], key=lambda x: x['minute']):
                            st.write(f"• {detail['minute']}' - vs {detail['opponent']} ({detail['score']}) - {detail['stage'].title()}")
                            st.write(f"  {detail['assist']}")
                    
                    with col2:
                        st.metric("Total Goals", data['goals'])
                        st.metric("Matches Scored In", len(data['matches']))
                        st.metric("Goals per Match", f"{data['goals']/len(data['matches']):.1f}")
        else:
            st.info("No goals scored yet")
        
        # NEW: MATCH HISTORY SECTION
        st.subheader("📅 Match History")
        if matches:
            # Sort matches by date or stage
            completed_matches = [m for m in matches if m.get('status') == 'completed']
            
            if completed_matches:
                for match in reversed(completed_matches[-10:]):  # Show last 10 matches
                    flag_a = COUNTRY_FLAGS.get(match.get('teamA_name', 'Team A'), "🏴")
                    flag_b = COUNTRY_FLAGS.get(match.get('teamB_name', 'Team B'), "🏴")
                    
                    with st.expander(f"{flag_a} {match['teamA_name']} {match['scoreA']}-{match['scoreB']} {match['teamB_name']} {flag_b} - {match.get('stage', 'Unknown').title()}", expanded=False):
                        
                        # Match summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**{match['teamA_name']}**")
                            st.write(f"Goals: {match['scoreA']}")
                        with col2:
                            st.write("**Match Info**")
                            st.write(f"Stage: {match.get('stage', 'Unknown').title()}")
                            st.write(f"Method: {match.get('method', 'Unknown').title()}")
                        with col3:
                            st.write(f"**{match['teamB_name']}**")
                            st.write(f"Goals: {match['scoreB']}")
                        
                        # Goal details with assists
                        st.write("**Goal Scorers:**")
                        goal_scorers = match.get('goal_scorers', [])
                        if goal_scorers:
                            # Sort goals by minute
                            sorted_goals = sorted(goal_scorers, key=lambda x: x['minute'])
                            
                            for goal in sorted_goals:
                                flag = COUNTRY_FLAGS.get(goal['team'], "🏴")
                                assist_info = goal.get('assist', 'Unassisted')
                                st.write(f"• {goal['minute']}' - {flag} **{goal['player']}** ({goal['team']}) - {assist_info}")
                        else:
                            st.info("No goal details available")
            else:
                st.info("No completed matches yet")
        else:
            st.info("No matches played yet")
            
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

# Database helper functions
def get_federations(query={}, **kwargs):
    """Safely get federations from database"""
    try:
        db = get_database()
        if db is None:
            return []
        return list(db.federations.find(query, **kwargs))
    except Exception:
        return []

def get_matches(query={}):
    """Safely get matches from database"""
    try:
        db = get_database()
        if db is None:
            return []
        return list(db.matches.find(query))
    except Exception:
        return []

def get_tournaments():
    """Safely get tournaments from database"""
    try:
        db = get_database()
        if db is None:
            return []
        return list(db.tournaments.find({}))
    except Exception:
        return []

if __name__ == "__main__":
    main()
