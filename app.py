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

# ... (keep all the other functions exactly the same as before)

# The rest of your functions remain unchanged (show_tournament_bracket, show_match_control, etc.)
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
