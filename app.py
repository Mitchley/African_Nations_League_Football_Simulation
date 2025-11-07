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
    .main-header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 2.5rem; border-radius: 20px; color: white; text-align: center; margin-bottom: 2rem; border: 4px solid #FFD700; box-shadow: 0 8px 25px rgba(0,0,0,0.2); }
    .feature-card { background: #ffffff; border-radius: 15px; padding: 1.5rem; margin: 0.5rem; border: 2px solid #2a5298; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: all 0.3s ease; height: 100%; color: #1a1a1a; }
    .feature-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.2); background: #f8f9fa; }
    .team-card { background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border-radius: 12px; padding: 1.5rem; margin: 0.5rem; border: 3px solid #1E3C72; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: transform 0.2s; color: #1a1a1a; }
    .team-card:hover { transform: translateY(-5px); box-shadow: 0 6px 15px rgba(0,0,0,0.15); }
    .match-card { background: #ffffff; border-radius: 10px; padding: 1.2rem; margin: 0.5rem 0; border-left: 5px solid #1E3C72; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #1a1a1a; border: 1px solid #e2e8f0; }
    .leaderboard-item { background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%); border-radius: 8px; padding: 1rem; margin: 0.3rem 0; border-left: 4px solid #FFD700; box-shadow: 0 2px 4px rgba(0,0,0,0.05); color: #1a1a1a; border: 1px solid #e2e8f0; }
    .progress-bar { background: #e2e8f0; border-radius: 10px; overflow: hidden; height: 20px; margin: 0.5rem 0; border: 1px solid #cbd5e0; }
    .progress-fill { background: linear-gradient(90deg, #1e3c72, #2a5298); height: 100%; transition: width 0.5s; }
    .tournament-bracket { background: #ffffff; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; border: 2px solid #2a5298; box-shadow: 0 4px 8px rgba(0,0,0,0.1); color: #1a1a1a; }
    .stage-header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center; margin: 1rem 0; font-weight: bold; border: 2px solid #FFD700; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display:none;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    try:
        initialize_database()
        if not st.session_state.get('user'):
            show_login_page()
        else:
            # Always set to Home Dashboard after login
            st.session_state.current_page = "🏠 Home Dashboard"
            show_app()
    except Exception as e:
        st.error(f"Application error: {str(e)}")

def show_login_page():
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color: #FFD700; font-size: 3em;">🏆 AFRICAN NATIONS LEAGUE</h1>
        <p style="margin:0; font-size: 1.5em; font-weight: bold;">Road to Glory 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🎯 What You Can Do")
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown("""<div class="feature-card"><h3>⚽ Realistic Match Simulation</h3><p>AI-powered matches with realistic outcomes</p></div>""", unsafe_allow_html=True)
    with col2: st.markdown("""<div class="feature-card"><h3>🌍 Represent Your Nation</h3><p>Lead your country to continental glory</p></div>""", unsafe_allow_html=True)
    with col3: st.markdown("""<div class="feature-card"><h3>📊 Live Tournament Tracking</h3><p>Follow the complete tournament bracket</p></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🔐 Get Started - Choose Your Role")
    
    tab1, tab2, tab3 = st.tabs(["👑 Admin Login", "🇺🇳 Federation Sign Up", "👀 Visitor Access"])
    with tab1:
        with st.form("admin_login"):
            email = st.text_input("Email", placeholder="admin@africanleague.com")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("🚀 Login as Admin", use_container_width=True):
                if login_user(email, password):
                    st.success("Welcome Admin!"); time.sleep(1); st.rerun()
                else: st.error("Invalid credentials")
    
    with tab2: show_federation_registration()
    
    with tab3:
        st.info("Explore tournament matches, standings, and statistics")
        if st.button("👀 Enter as Visitor", use_container_width=True, type="primary"):
            st.session_state.user = {"email": "visitor", "role": "visitor"}
            st.session_state.role = "visitor"
            st.session_state.current_page = "🏠 Home Dashboard"
            st.rerun()

def show_federation_registration():
    db = get_database()
    if db is None: st.error("❌ Cannot access database"); return
    
    team_count = get_team_count()
    st.info(f"📊 Teams registered: {team_count}/8")
    progress = min(team_count / 8 * 100, 100)
    st.markdown(f"""<div class="progress-bar"><div class="progress-fill" style="width: {progress}%"></div></div>""", unsafe_allow_html=True)
    
    if team_count >= 8: st.warning("🎯 Tournament full! New registrations will be waitlisted.")
    
    with st.form("register_team"):
        col1, col2 = st.columns(2)
        with col1: country = st.selectbox("Select Country", AFRICAN_COUNTRIES); manager = st.text_input("Manager Name")
        with col2: rep_name = st.text_input("Representative Name"); rep_email = st.text_input("Email"); password = st.text_input("Password", type="password")
        if st.form_submit_button("🚀 Register Federation", use_container_width=True):
            if register_federation(country, manager, rep_name, rep_email, password):
                st.success("Federation registered successfully!")
                if login_user(rep_email, password):
                    st.session_state.current_page = "🏠 Home Dashboard"; st.rerun()

def register_federation(country, manager, rep_name, rep_email, password):
    try:
        db = get_database()
        if db is None: st.error("Database unavailable"); return False
        existing_team = db.federations.find_one({"country": country})
        if existing_team: st.error("Country already registered"); return False
        if not register_user(rep_email, password, "federation", country): st.error("Registration failed"); return False
        
        squad = generate_realistic_squad()
        team_rating = sum(p["ratings"][p["naturalPosition"]] for p in squad) / len(squad)
        team_data = {"country": country, "manager": manager, "representative_name": rep_name, "representative_email": rep_email, "rating": round(team_rating, 2), "players": squad, "registered_at": datetime.now()}
        db.federations.insert_one(team_data)
        
        if get_team_count() >= 8:
            initialize_tournament(db); st.balloons(); st.success("🎊 Tournament started with 8 teams!")
        return True
    except Exception as e: st.error(f"Registration error: {str(e)}"); return False

def generate_realistic_squad():
    first_names = ["Mohamed", "Ibrahim", "Ahmed", "Youssef", "Samuel", "David", "Kwame", "Kofi", "Chukwu", "Adebayo", "Musa", "Said", "Rashid", "Tendai", "Blessing", "Prince", "Emmanuel", "Daniel", "Joseph", "Victor"]
    last_names = ["Traore", "Diallo", "Keita", "Camara", "Sow", "Diop", "Ndiaye", "Gueye", "Mensah", "Appiah", "Owusu", "Adeyemi", "Okafor", "Okoro", "Mohammed", "Ali", "Hussein", "Juma", "Kamau", "Nkosi"]
    squad = []; positions = {"GK": 3, "DF": 7, "MD": 8, "AT": 5}
    for pos, count in positions.items():
        for i in range(count):
            player_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            player = {"name": player_name, "naturalPosition": pos, "ratings": {p: random.randint(50, 100) if p == pos else random.randint(0, 50) for p in ["GK", "DF", "MD", "AT"]}, "isCaptain": False}
            squad.append(player)
    if squad: squad[0]["isCaptain"] = True
    return squad

def show_app():
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.user['email']}"); st.markdown(f"**Role:** {st.session_state.role.upper()}"); st.markdown("---")
        if st.session_state.role == "admin": pages = ["🏠 Home Dashboard", "🏆 Tournament Bracket", "⚽ Match Control", "📊 Analytics"]
        elif st.session_state.role == "federation": pages = ["🏠 Home Dashboard", "🏆 Tournament Bracket", "👥 My Team", "📊 Statistics"]
        else: pages = ["🏠 Home Dashboard", "🏆 Tournament Bracket", "📊 Statistics"]
        for page in pages:
            if st.button(page, use_container_width=True, type="primary" if st.session_state.get('current_page') == page else "secondary"):
                st.session_state.current_page = page; st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True): logout_user(); st.rerun()
    
    current_page = st.session_state.get('current_page', '🏠 Home Dashboard')
    if current_page == "🏠 Home Dashboard": show_home_dashboard()
    elif current_page == "🏆 Tournament Bracket": show_tournament_bracket()
    elif current_page == "⚽ Match Control": show_match_control()
    elif current_page == "👥 My Team": show_my_team()
    elif current_page == "📊 Analytics": show_analytics()
    elif current_page == "📊 Statistics": show_statistics()

def show_home_dashboard():
    db = get_database()
    if db is None: st.error("❌ Database connection failed"); return
    
    st.markdown("""<div class="main-header"><h1 style="margin:0; color: #FFD700; font-size: 2.8em;">🏆 WELCOME TO AFRICAN NATIONS LEAGUE 2024</h1><p style="margin:0; font-size: 1.3em; font-weight: bold;">Tournament Dashboard</p></div>""", unsafe_allow_html=True)
    
    teams = get_federations(); matches = get_matches(); completed_matches = [m for m in matches if m.get('status') == 'completed']
    tournament_data = get_tournaments(); tournament = tournament_data[0] if tournament_data else {}
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Teams", len(teams))
    with col2: st.metric("Matches Played", len(completed_matches))
    with col3: st.metric("Tournament Status", "Active" if tournament.get('status') == 'active' else "Ready")
    with col4: st.metric("Current Stage", tournament.get('current_stage', 'Not Started').replace('_', ' ').title())
    
    st.markdown("---")
    if teams:
        st.subheader("🇺🇳 Currently Registered Teams")
        cols = st.columns(4)
        for i, team in enumerate(teams):
            with cols[i % 4]:
                flag = COUNTRY_FLAGS.get(team['country'], "🏴"); rating = team.get('rating', 75)
                st.markdown(f"""<div class="team-card"><h3 style="margin:0; font-size: 2em;">{flag}</h3><h4 style="margin:5px 0; color: #1E3C72;">{team['country']}</h4><p style="margin:0; color: #666; font-size: 0.9em;">Rating: {rating}</p></div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("---"); st.subheader("📅 Recent Matches")
        if completed_matches:
            for match in reversed(completed_matches[-5:]):
                flag_a = COUNTRY_FLAGS.get(match.get('teamA_name', 'Team A'), "🏴"); flag_b = COUNTRY_FLAGS.get(match.get('teamB_name', 'Team B'), "🏴")
                st.markdown(f"""<div class="match-card"><div style="display: flex; justify-content: space-between; align-items: center;"><span><strong>{flag_a} {match.get('teamA_name', 'Team A')}</strong></span><span><strong>{match.get('scoreA', 0)} - {match.get('scoreB', 0)}</strong></span><span><strong>{match.get('teamB_name', 'Team B')} {flag_b}</strong></span></div></div>""", unsafe_allow_html=True)
        else: st.info("No matches played yet")
    
    with col2:
        st.subheader("📈 Tournament Progress")
        total_matches = len(matches); completed_count = len(completed_matches)
        if total_matches > 0:
            progress = (completed_count / total_matches) * 100
            st.markdown(f"""<div class="progress-bar"><div class="progress-fill" style="width: {progress}%"></div></div><div style="text-align: center; font-weight: bold;">{completed_count}/{total_matches} matches ({progress:.0f}%)</div>""", unsafe_allow_html=True)
        else: st.info("Tournament not started")
        
        stage_info = {'quarterfinal': '🎯 Quarter Finals - 4 matches', 'semifinal': '🔥 Semi Finals - 2 matches', 'final': '🏆 Grand Final - 1 match', 'Not Started': '⏳ Tournament ready to start'}
        st.info(f"**Current Stage:** {stage_info.get(tournament.get('current_stage', 'Not Started'), 'Not Started')}")
        
        st.markdown("---"); st.subheader("🏅 Team Leaderboard")
        if teams:
            for i, team in enumerate(teams[:5]):
                flag = COUNTRY_FLAGS.get(team['country'], "🏴"); medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                st.markdown(f"""<div class="leaderboard-item"><div style="display: flex; justify-content: space-between; align-items: center;"><span><strong>{medal} {flag} {team['country']}</strong></span><span style="color: #1E3C72; font-weight: bold;">{team.get('rating', 75)}</span></div></div>""", unsafe_allow_html=True)
        else: st.info("No teams yet")
    
    if st.session_state.role == 'admin' and len(teams) >= 8:
        st.markdown("---"); st.subheader("⚡ Admin Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Start Tournament", use_container_width=True):
                db = get_database(); initialize_tournament(db) if db is not None else None; st.rerun()
        with col2:
            if st.button("⚡ Simulate All", use_container_width=True):
                db = get_database(); simulate_all_matches(db) if db is not None else None; st.rerun()
        with col3:
            if st.button("📊 View Full Bracket", use_container_width=True):
                st.session_state.current_page = "🏆 Tournament Bracket"; st.rerun()

def show_tournament_bracket():
    st.markdown("""<div class="main-header"><h1 style="margin:0; color: #FFD700; font-size: 2.5em;">🏆 AFRICAN NATIONS LEAGUE 2025</h1><p style="margin:0; font-size: 1.3em; font-weight: bold;">ROAD TO THE FINAL</p></div>""", unsafe_allow_html=True)
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

# ... rest of the functions remain the same (show_match_control, play_match_with_commentary, etc.)

# Database helper functions
def get_federations(query={}, **kwargs):
    try: db = get_database(); return list(db.federations.find(query, **kwargs)) if db is not None else []
    except Exception: return []

def get_matches(query={}):
    try: db = get_database(); return list(db.matches.find(query)) if db is not None else []
    except Exception: return []

def get_tournaments():
    try: db = get_database(); return list(db.tournaments.find({})) if db is not None else []
    except Exception: return []

if __name__ == "__main__":
    main()
