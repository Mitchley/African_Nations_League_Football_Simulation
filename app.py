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
            # Set Home as default landing page for all users after login
            if 'current_page' not in st.session_state:
                st.session_state.current_page = "🏠 Home"
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
    
    tab1, tab2, tab3 = st.tabs([" Admin Login", "Federation Sign Up", " Visitor Access"])
    with tab1:
        with st.form("admin_login"):
            email = st.text_input("Email", placeholder="admin@africanleague.com")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login as Admin", use_container_width=True):
                if login_user(email, password):
                    st.success("Welcome Admin!")
                    # FIX: Set current_page for admin
                    st.session_state.current_page = "🏠 Home"
                    time.sleep(1)
                    st.rerun()
                else: 
                    st.error("Invalid credentials")
    
    with tab2: 
        show_federation_registration()
    
    with tab3:
        st.info("Explore tournament matches, standings, and statistics")
        if st.button("Enter as Visitor", use_container_width=True, type="primary"):
            st.session_state.user = {"email": "visitor", "role": "visitor"}
            st.session_state.role = "visitor"
            st.session_state.current_page = "🏠 Home"  # This works for visitors
            st.rerun()
def show_federation_registration():
    db = get_database()
    if db is None: st.error("❌ Cannot access database"); return
    
    team_count = get_team_count()
    #st.info(f"📊 Teams registered: {team_count}/8")
    progress = min(team_count / 8 * 100, 100)
    #st.markdown(f"""<div class="progress-bar"><div class="progress-fill" style="width: {progress}%"></div></div>""", unsafe_allow_html=True)
    
    if team_count >= 8: st.warning("Tournament full! New registrations will be waitlisted.")
    
    with st.form("register_team"):
        col1, col2 = st.columns(2)
        with col1: 
            country = st.selectbox("Select Country", AFRICAN_COUNTRIES)
            manager = st.text_input("Manager Name")
        with col2: 
            rep_name = st.text_input("Representative Name")
            rep_email = st.text_input("Email")
            password = st.text_input("Password", type="password")
        
        # Player Management Section
        st.markdown("---")
        st.subheader("Manage Your Squad")
        
        # Option to auto-generate or manually add players
        player_option = st.radio("Player Selection:", ["Auto-generate Squad", "Add Players Manually"])
        
        squad = []
        if player_option == "Add Players Manually":
            st.info("💡 Add at least 11 players (1 GK, 4 DF, 4 MD, 3 AT recommended)")
            
            # Position counters
            gk_count = 0
            df_count = 0
            md_count = 0
            at_count = 0
            
            # Add players dynamically
            num_players = st.number_input("Number of players to add:", min_value=11, max_value=23, value=15)
            
            for i in range(num_players):
                st.markdown(f"### Player {i+1}")
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    player_name = st.text_input(f"Player Name {i+1}", placeholder="e.g., Mohamed Salah", key=f"name_{i}")
                
                with col2:
                    position = st.selectbox(f"Position {i+1}", ["GK", "DF", "MD", "AT"], key=f"pos_{i}")
                    # Update counters
                    if position == "GK": gk_count += 1
                    elif position == "DF": df_count += 1
                    elif position == "MD": md_count += 1
                    elif position == "AT": at_count += 1
                
                with col3:
                    rating = st.slider(f"Rating {i+1}", 50, 100, 75, key=f"rating_{i}")
                
                if player_name:  # Only add if player has a name
                    player_data = {
                        "name": player_name,
                        "naturalPosition": position,
                        "ratings": {
                            "GK": rating if position == "GK" else random.randint(30, 60),
                            "DF": rating if position == "DF" else random.randint(30, 60),
                            "MD": rating if position == "MD" else random.randint(30, 60),
                            "AT": rating if position == "AT" else random.randint(30, 60)
                        },
                        "isCaptain": False
                    }
                    squad.append(player_data)
            
            # Show squad composition
            st.markdown("---")
            st.subheader("📊 Squad Composition")
            comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)
            with comp_col1: st.metric("Goalkeepers", gk_count)
            with comp_col2: st.metric("Defenders", df_count)
            with comp_col3: st.metric("Midfielders", md_count)
            with comp_col4: st.metric("Attackers", at_count)
            
            # Validate squad composition
            if gk_count < 1:
                st.error("❌ Need at least 1 Goalkeeper")
            if df_count < 4:
                st.warning("⚠️ Recommended: At least 4 Defenders")
            if md_count < 4:
                st.warning("⚠️ Recommended: At least 4 Midfielders")
            if at_count < 3:
                st.warning("⚠️ Recommended: At least 3 Attackers")
            
            # Set captain
            if squad:
                captain_options = [f"{i+1}. {p['name']} ({p['naturalPosition']})" for i, p in enumerate(squad)]
                selected_captain = st.selectbox("Select Team Captain:", captain_options)
                captain_index = int(selected_captain.split('.')[0]) - 1
                squad[captain_index]["isCaptain"] = True
                st.success(f"✅ Captain set: {squad[captain_index]['name']}")
        
        else:  # Auto-generate squad
            #st.info("A balanced squad of 23 players will be automatically generated")
            squad = generate_realistic_squad()
        
        if st.form_submit_button("Register Federation", use_container_width=True):
            if not squad and player_option == "Add Players Manually":
                st.error("Please add players to your squad")
            elif gk_count < 1 and player_option == "Add Players Manually":
                st.error("Need at least 1 Goalkeeper")
            else:
                if register_federation(country, manager, rep_name, rep_email, password, squad):
                    st.success("Federation registered successfully!")
                    if login_user(rep_email, password):
                        st.session_state.current_page = "🏠 Home"
                        st.rerun()
def register_federation(country, manager, rep_name, rep_email, password, custom_squad=None):
    try:
        db = get_database()
        if db is None: st.error("Database unavailable"); return False
        existing_team = db.federations.find_one({"country": country})
        if existing_team: st.error("Country already registered"); return False
        if not register_user(rep_email, password, "federation", country): st.error("Registration failed"); return False
        
        # Use custom squad if provided, otherwise generate one
        if custom_squad:
            squad = custom_squad
        else:
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
        
        # Set current_page for federation users after registration/login
        if login_user(rep_email, password):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
        return True
    except Exception as e: 
        st.error(f"Registration error: {str(e)}")
        return False
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
        # Updated page names with "Home" instead of "Home Dashboard"
        if st.session_state.role == "admin": pages = ["🏠 Home", "🏆 Tournament Bracket", "⚽ Match Control", "📊 Analytics"]
        elif st.session_state.role == "federation": pages = ["🏠 Home", "🏆 Tournament Bracket", "👥 My Team", "📊 Statistics"]
        else: pages = ["🏠 Home", "🏆 Tournament Bracket", "📊 Statistics"]
        for page in pages:
            if st.button(page, use_container_width=True, type="primary" if st.session_state.get('current_page') == page else "secondary"):
                st.session_state.current_page = page; st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True): logout_user(); st.rerun()
    
    # Ensure Home is the default page after login
    if 'current_page' not in st.session_state or st.session_state.current_page is None:
        st.session_state.current_page = "🏠 Home"
    
    current_page = st.session_state.get('current_page', '🏠 Home')
    # Updated function calls to use "Home" instead of "Home Dashboard"
    if current_page == "🏠 Home": show_home_dashboard()
    elif current_page == "🏆 Tournament Bracket": show_tournament_bracket()
    elif current_page == "⚽ Match Control": show_match_control()
    elif current_page == "👥 My Team": show_my_team()
    elif current_page == "📊 Analytics": show_analytics()
    elif current_page == "📊 Statistics": show_statistics()
def show_home_dashboard():
    db = get_database()
    if db is None: st.error("❌ Database connection failed"); return
    
    st.markdown("""<div class="main-header"><h1 style="margin:0; color: #FFD700; font-size: 2.8em;">🏆 WELCOME TO AFRICAN NATIONS LEAGUE 2025</h1><p style="margin:0; font-size: 1.3em; font-weight: bold;">Tournament Dashboard</p></div>""", unsafe_allow_html=True)
    
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
    db = get_database(); show_enhanced_tournament_bracket(db) if db is not None else st.error("❌ Database unavailable")

def show_enhanced_tournament_bracket(db):
    matches = get_matches(); tournament_data = get_tournaments(); tournament = tournament_data[0] if tournament_data else {}
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Tournament Stage", tournament.get('current_stage', 'Not Started').replace('_', ' ').title())
    with col2: st.metric("Matches Completed", f"{len([m for m in matches if m.get('status') == 'completed'])}/{len(matches)}")
    with col3: st.metric("Status", "🏃‍♂️ LIVE" if tournament.get('status') == 'active' else "⏳ READY")
    
    st.markdown("---")
    if not matches:
        st.info("🎯 Tournament not started. Admin can start when 8 teams are registered.")
        teams = get_federations()
        if len(teams) >= 8:
            st.subheader("🎊 Ready to Start! Here's how the bracket would look:")
            random.shuffle(teams); col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.markdown('<div class="stage-header">QUARTER FINALS</div>', unsafe_allow_html=True)
                for i in range(0, 8, 2):
                    flag1 = COUNTRY_FLAGS.get(teams[i]['country'], "🏴"); flag2 = COUNTRY_FLAGS.get(teams[i+1]['country'], "🏴")
                    st.markdown(f"""<div class="tournament-bracket"><div style="text-align: center; font-weight: bold; margin-bottom: 10px;">Match {i//2 + 1}</div><div style="text-align: center; font-size: 1.1em;">{flag1} {teams[i]['country']}</div><div style="text-align: center; margin: 8px 0; font-weight: bold;">VS</div><div style="text-align: center; font-size: 1.1em;">{flag2} {teams[i+1]['country']}</div></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="stage-header">SEMI FINALS</div>', unsafe_allow_html=True); st.info("Winners from Quarter-Finals will advance here")
                for i in range(2): st.markdown(f"""<div class="tournament-bracket"><div style="text-align: center; color: #666; padding: 2rem;">Semi-Final {i+1}<br><small>Waiting for Quarter-Finals</small></div></div>""", unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="stage-header">GRAND FINAL</div>', unsafe_allow_html=True)
                st.markdown("""<div class="tournament-bracket"><div style="text-align: center; color: #666; padding: 2rem;">🏆 Championship Match<br><small>Winners from Semi-Finals</small></div></div>""", unsafe_allow_html=True)
        return
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown('<div class="stage-header">QUARTER FINALS</div>', unsafe_allow_html=True)
        quarter_matches = [m for m in matches if m.get('stage') == 'quarterfinal']
        if not quarter_matches: st.info("⏳ Quarter-finals not created")
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
                    # Handle NULL team names when determining winners
                    team_a = match.get('teamA_name') or "TBD"
                    team_b = match.get('teamB_name') or "TBD"
                    winner = team_a if match['scoreA'] > match['scoreB'] else team_b
                    winners.append(winner)
                
                for i in range(0, 4, 2):
                    flag1 = COUNTRY_FLAGS.get(winners[i], "🏴") if winners[i] != "TBD" else "❓"
                    flag2 = COUNTRY_FLAGS.get(winners[i+1], "🏴") if winners[i+1] != "TBD" else "❓"
                    st.markdown(f"""<div class="tournament-bracket" style="background: #e3f2fd;"><div style="text-align: center; font-weight: bold;">Semi-Final {i//2 + 1}</div><div style="text-align: center; margin: 10px 0;">{flag1} {winners[i]}</div><div style="text-align: center; margin: 8px 0; font-weight: bold;">VS</div><div style="text-align: center; margin: 10px 0;">{flag2} {winners[i+1]}</div><div style="text-align: center; color: #1976d2; font-size: 0.9em;">Ready to be created</div></div>""", unsafe_allow_html=True)
            else: st.info("⏳ Waiting for quarter-final results...")
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
                    # Handle NULL team names when determining winners
                    team_a = match.get('teamA_name') or "TBD"
                    team_b = match.get('teamB_name') or "TBD"
                    winner = team_a if match['scoreA'] > match['scoreB'] else team_b
                    winners.append(winner)
                
                flag1 = COUNTRY_FLAGS.get(winners[0], "🏴") if winners[0] != "TBD" else "❓"
                flag2 = COUNTRY_FLAGS.get(winners[1], "🏴") if winners[1] != "TBD" else "❓"
                st.markdown(f"""<div class="tournament-bracket" style="background: #fff3cd; border: 2px solid #FFD700;"><div style="text-align: center; font-weight: bold; color: #856404;">🏆 CHAMPIONSHIP</div><div style="text-align: center; margin: 15px 0; font-size: 1.1em;">{flag1} {winners[0]}</div><div style="text-align: center; margin: 10px 0; font-weight: bold; font-size: 1.2em;">VS</div><div style="text-align: center; margin: 15px 0; font-size: 1.1em;">{flag2} {winners[1]}</div><div style="text-align: center; color: #856404; font-size: 0.9em;">Ready to be created</div></div>""", unsafe_allow_html=True)
            else: st.info("⏳ Waiting for semi-final results...")
        else:
            final_match = final_matches[0]
            if final_match.get('status') == 'completed':
                # Handle NULL team names in final match
                team_a_name = final_match.get('teamA_name') or "TBD"
                team_b_name = final_match.get('teamB_name') or "TBD"
                winner = team_a_name if final_match['scoreA'] > final_match['scoreB'] else team_b_name
                winner_flag = COUNTRY_FLAGS.get(winner, "🏆") if winner != "TBD" else "🏆"
                
                # CHANGED: Final score now in blue color for better visibility
                st.markdown(f"""<div style="background: linear-gradient(135deg, #FFD700 0%, #FFEC8B 100%); padding: 2rem; border-radius: 15px; text-align: center; border: 3px solid #1E3C72; margin-top: 1rem;"><h2 style="color: #1E3C72; margin: 0;">🏆 TOURNAMENT CHAMPION 🏆</h2><h1 style="color: #1E3C72; margin: 1rem 0; font-size: 2.5em;">{winner_flag} {winner}</h1><p style="color: #1E3C72; margin: 0; font-size: 1.1em;">African Nations League 2025 Winner</p><div style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.5); border-radius: 10px;"><strong style="color: #1E3C72; font-size: 1.2em;">Final Score: {team_a_name} {final_match['scoreA']} - {final_match['scoreB']} {team_b_name}</strong></div></div>""", unsafe_allow_html=True)
            else: display_enhanced_match_card(final_match, "FINAL", "CHAMPION")
def display_enhanced_match_card(match, match_label, next_round):
    # Handle NULL/None team names by providing defaults
    team_a_name = match.get('teamA_name') or "TBD"
    team_b_name = match.get('teamB_name') or "TBD"
    
    # Use flags only for valid team names, otherwise use placeholder
    flag_a = COUNTRY_FLAGS.get(team_a_name, "🏴") if team_a_name != "TBD" else "❓"
    flag_b = COUNTRY_FLAGS.get(team_b_name, "🏴") if team_b_name != "TBD" else "❓"
    
    if match.get('status') == 'completed':
        winner = team_a_name if match['scoreA'] > match['scoreB'] else team_b_name
        winner_flag = flag_a if match['scoreA'] > match['scoreB'] else flag_b
        st.markdown(f"""<div class="tournament-bracket" style="background: #d4edda;"><div style="text-align: center; font-weight: bold; color: #155724;">{match_label}</div><div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;"><span>{flag_a} {team_a_name}</span><span style="font-weight: bold; font-size: 1.2em;">{match['scoreA']}</span></div><div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;"><span>{flag_b} {team_b_name}</span><span style="font-weight: bold; font-size: 1.2em;">{match['scoreB']}</span></div><div style="text-align: center; margin-top: 10px; padding: 8px; background: #c3e6cb; border-radius: 5px;"><strong>➡️ Advances to {next_round}: {winner_flag} {winner}</strong></div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="tournament-bracket"><div style="text-align: center; font-weight: bold; color: #1E3C72;">{match_label}</div><div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;"><span style="font-weight: bold;">{flag_a} {team_a_name}</span><span style="font-weight: bold;">VS</span></div><div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;"><span style="font-weight: bold;">{flag_b} {team_b_name}</span><span style="font-size: 1.2em;">⏰</span></div><div style="text-align: center; margin-top: 10px; color: #666; font-size: 0.9em;">Winner advances to {next_round}</div></div>""", unsafe_allow_html=True)

def show_match_control():
    if st.session_state.role != 'admin': st.error("🔒 Admin access required"); return
    st.title("⚽ Match Control Center"); db = get_database()
    if db is None: st.error("Database unavailable"); return
    
    st.subheader("🎯 Tournament Management")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Start Tournament", use_container_width=True): initialize_tournament(db); st.rerun()
    with col2:
        if st.button("🔄 Reset Tournament", use_container_width=True):
            try: db.matches.delete_many({}); db.tournaments.delete_many({}); st.success("Tournament reset!"); st.rerun()
            except Exception as e: st.error(f"Reset failed: {str(e)}")
    with col3:
        if st.button("⚡ Auto Simulate All", use_container_width=True): simulate_all_matches(db); st.rerun()
    
    st.subheader("🎮 Match Simulation")
    scheduled_matches = get_matches({"status": "scheduled"})
    if scheduled_matches:
        for match in scheduled_matches:
            st.write(f"**{match['teamA_name']} vs {match['teamB_name']}** ({match.get('stage', 'unknown')})")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Play with Commentary", key=f"play_{match['_id']}"): play_match_with_commentary(match)
            with col2:
                if st.button(f"Quick Simulate", key=f"quick_{match['_id']}"): simulate_match_quick(match)
            st.markdown("---")
    else: st.info("No scheduled matches available")

def play_match_with_commentary(match):
    try:
        db = get_database()
        if db is None: st.error("Database unavailable"); return
        score_a, score_b, goal_scorers, commentary = simulate_match_realistic(db, match["_id"], match['teamA_name'], match['teamB_name'])
        st.success(f"**Final: {match['teamA_name']} {score_a}-{score_b} {match['teamB_name']}**")
        with st.expander("📝 Match Commentary", expanded=True):
            for comment in commentary: st.success(f"🎯 {comment}") if "GOAL!" in comment else st.info(f"↪️ {comment}") if "Assist" in comment else st.write(f"• {comment}")
        if goal_scorers:
            st.subheader("🥅 Goal Scorers")
            for goal in sorted(goal_scorers, key=lambda x: x['minute']):
                flag = COUNTRY_FLAGS.get(goal['team'], "🏴"); assist_info = goal.get('assist', 'Unassisted')
                st.write(f"**{goal['minute']}'** - {flag} **{goal['player']}** *({assist_info})*") if "Assist:" in assist_info else st.write(f"**{goal['minute']}'** - {flag} **{goal['player']}** (Solo goal)")
        db.matches.update_one({"_id": match["_id"]}, {"$set": {"status": "completed", "scoreA": score_a, "scoreB": score_b, "goal_scorers": goal_scorers, "method": "commentary"}})
        advance_tournament(db, match); st.rerun()
    except Exception as e: st.error(f"Match simulation error: {str(e)}"); simulate_match_quick(match)

def simulate_match_realistic(db, match_id, team_a_name, team_b_name):
    # Get actual players from players collection
    players_a = list(db.players.find({"country": team_a_name}))
    players_b = list(db.players.find({"country": team_b_name}))
    
    score_a = random.randint(0, 3); score_b = random.randint(0, 3)
    commentary = []; goal_scorers = []
    commentary.append(f"Match between {team_a_name} and {team_b_name} begins!")
    
    def get_goal_event(players, team_name, minute):
        if players:
            field_players = [p for p in players if p.get('naturalPosition') != 'GK']
            if field_players:
                scorer = random.choice(field_players)
                has_assist = random.random() < 0.7
                if has_assist:
                    possible_assisters = [p for p in field_players if p.get('name') != scorer.get('name')]
                    if possible_assisters: assister = random.choice(possible_assisters); assist_text = f"Assist: {assister.get('name')}"
                    else: assist_text = "Solo goal"
                else: assist_text = "Solo goal"
                return {"player": scorer.get('name'), "minute": minute, "team": team_name, "assist": assist_text}
        return {"player": f"Player {random.randint(1, 23)}", "minute": minute, "team": team_name, "assist": "Unassisted"}
    
    for i in range(score_a):
        minute = random.randint(1, 90); goal = get_goal_event(players_a, team_a_name, minute); goal_scorers.append(goal)
        commentary.append(f"{minute}' - GOAL! {goal['player']} scores for {team_a_name}!")
        if "Assist:" in goal['assist']: commentary.append(f"    Great work by {goal['assist'].replace('Assist: ', '')} to set up the goal!")
    
    for i in range(score_b):
        minute = random.randint(1, 90); goal = get_goal_event(players_b, team_b_name, minute); goal_scorers.append(goal)
        commentary.append(f"{minute}' - GOAL! {goal['player']} scores for {team_b_name}!")
        if "Assist:" in goal['assist']: commentary.append(f"    Beautiful assist from {goal['assist'].replace('Assist: ', '')}!")
    
    commentary.append("What an exciting match!" if score_a + score_b > 0 else "A defensive battle ends goalless.")
    commentary.append("Full time!")
    return score_a, score_b, goal_scorers, commentary

def simulate_match_quick(match):
    db = get_database()
    if db is None: st.error("Database unavailable"); return
    score_a = random.randint(0, 3); score_b = random.randint(0, 3)
    
    # Get actual players from players collection
    players_a = list(db.players.find({"country": match['teamA_name']}))
    players_b = list(db.players.find({"country": match['teamB_name']}))
    
    goal_scorers = []
    def create_quick_goal(players, team_name, minute):
        if players:
            field_players = [p for p in players if p.get('naturalPosition') != 'GK']
            if field_players:
                scorer = random.choice(field_players)
                has_assist = random.random() < 0.6
                if has_assist:
                    possible_assisters = [p for p in field_players if p.get('name') != scorer.get('name')]
                    if possible_assisters: assister = random.choice(possible_assisters); assist_text = f"Assist: {assister.get('name')}"
                    else: assist_text = "Solo goal"
                else: assist_text = "Solo goal"
                return {"player": scorer.get('name'), "minute": minute, "team": team_name, "assist": assist_text}
        return {"player": f"Player {random.randint(1, 23)}", "minute": minute, "team": team_name, "assist": "Unassisted"}
    
    for i in range(score_a): goal_scorers.append(create_quick_goal(players_a, match['teamA_name'], random.randint(1, 90)))
    for i in range(score_b): goal_scorers.append(create_quick_goal(players_b, match['teamB_name'], random.randint(1, 90)))
    goal_scorers.sort(key=lambda x: x['minute'])
    
    try:
        db.matches.update_one({"_id": match["_id"]}, {"$set": {"status": "completed", "scoreA": score_a, "scoreB": score_b, "goal_scorers": goal_scorers, "method": "simulated"}})
        advance_tournament(db, match); st.success(f"Match simulated: {match['teamA_name']} {score_a}-{score_b} {match['teamB_name']}"); st.rerun()
    except Exception as e: st.error(f"Simulation failed: {str(e)}")

def initialize_tournament(db):
    try:
        teams = list(db.federations.find({}).limit(8))
        if len(teams) < 8: st.error(f"Need 8 teams. Currently: {len(teams)}"); return
        random.shuffle(teams); db.matches.delete_many({})
        for i in range(0, 8, 2):
            match_data = {"teamA_name": teams[i]["country"], "teamB_name": teams[i+1]["country"], "stage": "quarterfinal", "status": "scheduled", "scoreA": 0, "scoreB": 0, "created_at": datetime.now()}
            db.matches.insert_one(match_data)
        db.tournaments.update_one({}, {"$set": {"status": "active", "current_stage": "quarterfinal"}}, upsert=True)
        st.success("🎊 Tournament started! Quarter-finals created.")
    except Exception as e: st.error(f"Tournament start failed: {str(e)}")

def advance_tournament(db, completed_match):
    try:
        stage = completed_match.get('stage'); all_matches = list(db.matches.find({"stage": stage}))
        if all(m.get('status') == 'completed' for m in all_matches):
            if stage == "quarterfinal": create_semifinals(db)
            elif stage == "semifinal": create_final(db)
    except Exception as e: st.error(f"Tournament advancement failed: {str(e)}")

def create_semifinals(db):
    try:
        quarters = list(db.matches.find({"stage": "quarterfinal", "status": "completed"}))
        winners = [match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name'] for match in quarters]
        for i in range(0, 4, 2):
            match_data = {"teamA_name": winners[i], "teamB_name": winners[i+1], "stage": "semifinal", "status": "scheduled", "scoreA": 0, "scoreB": 0, "created_at": datetime.now()}
            db.matches.insert_one(match_data)
        db.tournaments.update_one({}, {"$set": {"current_stage": "semifinal"}}); st.success("Semi-finals created!")
    except Exception as e: st.error(f"Semi-final creation failed: {str(e)}")

def create_final(db):
    try:
        semis = list(db.matches.find({"stage": "semifinal", "status": "completed"}))
        winners = [match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name'] for match in semis]
        match_data = {"teamA_name": winners[0], "teamB_name": winners[1], "stage": "final", "status": "scheduled", "scoreA": 0, "scoreB": 0, "created_at": datetime.now()}
        db.matches.insert_one(match_data); db.tournaments.update_one({}, {"$set": {"current_stage": "final"}}); st.success("Final match created!")
    except Exception as e: st.error(f"Final creation failed: {str(e)}")

def simulate_all_matches(db):
    try:
        scheduled = list(db.matches.find({"status": "scheduled"}))
        for match in scheduled: simulate_match_quick(match)
        st.success("All matches simulated!")
    except Exception as e: st.error(f"Simulation failed: {str(e)}")

def show_my_team():
    if st.session_state.role != 'federation': st.info("Federation access required"); return
    db = get_database()
    if db is None: st.error("Database unavailable"); return
    try: user_team = db.federations.find_one({"representative_email": st.session_state.user['email']})
    except Exception as e: st.error(f"Error loading team data: {str(e)}"); return
    if user_team:
        st.title(f"👥 {user_team['country']} National Team")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Manager", user_team.get('manager', 'Unknown'))
        with col2: st.metric("Team Rating", user_team.get('rating', 75))
        with col3: st.metric("Squad Size", f"{len(user_team.get('players', []))}/23")
        st.subheader("Team Squad")
        for pos in ["GK", "DF", "MD", "AT"]:
            players = [p for p in user_team.get('players', []) if p['naturalPosition'] == pos]
            if players:
                with st.expander(f"{pos} - {len(players)} players"):
                    for player in players: st.write(f"**{player['name']}** - Rating: {player['ratings'][player['naturalPosition']]}{' ⭐' if player.get('isCaptain') else ''}")
    else: st.error("No team found")

def show_analytics(): show_statistics_content(True) if st.session_state.role == 'admin' else st.error("Admin access required")
def show_statistics(): show_statistics_content(False)

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
                for i, team in enumerate(teams):
                    flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                    st.markdown(f"""<div style="background: {'#fff3cd' if i < 3 else 'white'}; padding: 0.8rem; margin: 0.3rem 0; border-radius: 8px; border-left: 4px solid {'#FFD700' if i < 3 else '#1E3C72'};"><div style="display: flex; justify-content: space-between; align-items: center;"><span><strong>{medal} {flag} {team['country']}</strong></span><span style="color: #1E3C72; font-weight: bold; font-size: 1.1em;">{team.get('rating', 75)}</span></div></div>""", unsafe_allow_html=True)
            with col2:
                if len(teams) >= 3:
                    for i in range(min(3, len(teams))):
                        team = teams[i]
                        flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                        st.metric(f"{['🥇', '🥈', '🥉'][i]} {team['country']}", f"Rating: {team.get('rating', 75)}")
        else:
            st.info("No teams registered yet")
        
        st.subheader("📅 Match History")
        # Get matches here - this was missing!
        matches = list(db.matches.find({}))
        
        if matches:
            completed_matches = [m for m in matches if m.get('status') == 'completed']
            if completed_matches:
                for match in reversed(completed_matches[-10:]):
                    flag_a = COUNTRY_FLAGS.get(match.get('teamA_name', 'Team A'), "🏴")
                    flag_b = COUNTRY_FLAGS.get(match.get('teamB_name', 'Team B'), "🏴")
                    with st.expander(f"{flag_a} {match['teamA_name']} {match['scoreA']}-{match['scoreB']} {match['teamB_name']} {flag_b} - {match.get('stage', 'Unknown').title()}", expanded=False):
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
                        st.write("**Goal Scorers:**")
                        goal_scorers = match.get('goal_scorers', [])
                        if goal_scorers:
                            for goal in sorted(goal_scorers, key=lambda x: x['minute']):
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
