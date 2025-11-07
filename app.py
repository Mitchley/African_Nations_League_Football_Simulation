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
        <p style="margin:0; font-size: 1em;">Tournament Ready with 8 Teams! 🎉</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 **Admin Login**", "🇺🇳 **Federation Sign Up**", "👤 **Visitor Access**"])
    
    with tab1: show_admin_login()
    with tab2: show_federation_registration()
    with tab3: show_visitor_access()

def show_admin_login():
    st.subheader("Admin Login")
    st.success("🎊 Tournament Ready! 8 teams are registered and waiting.")
    
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
    st.success("🏆 Tournament is live! Watch matches and follow the action.")
    
    if st.button("👀 **Enter as Visitor**", use_container_width=True, type="primary"):
        st.session_state.user = {"email": "visitor@africanleague.com", "role": "visitor"}
        st.session_state.role = "visitor"
        st.success("🎉 Welcome to the African Nations League!")
        time.sleep(1)
        st.rerun()

def show_federation_registration():
    st.subheader("🇺🇳 Federation Registration")
    
    db = get_database()
    
    # Check current team count
    existing_teams = db.federations.count_documents({}) if db else 0
    
    if existing_teams >= 8:
        st.warning("⚠️ Tournament is full with 8 teams! New registrations will be waitlisted.")
        st.info("You can still register, but your team will join the next tournament edition.")
    else:
        st.info(f"📊 Current teams in database: {existing_teams}/8")
    
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
        # Calculate current position counts
        pos_count = {'GK': 0, 'DF': 0, 'MD': 0, 'AT': 0}
        for player in squad:
            pos_count[player.position] += 1
        
        # Only show available positions
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
                # Generate ratings according to requirements
                ratings = generate_player_ratings(position)
                
                # Create Player object
                new_player = Player(player_name, position)
                # Store ratings in session state
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
    
    # Show squad requirements
    if len(squad) < 23:
        st.warning(f"**Need {23 - len(squad)} more players** (3 GK, 7 DF, 8 MD, 5 AT)")
    
    # Show current squad
    if squad:
        # Captain selection when squad is complete
        if len(squad) == 23:
            captain_options = [f"{p.name} ({p.position})" for p in squad]
            selected_captain = st.selectbox("Select Captain", captain_options, key="captain_select")
            captain_index = captain_options.index(selected_captain)
            
            for i, player in enumerate(squad):
                player.is_captain = (i == captain_index)
        
        # Show players by position
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
                        # Show player's natural position rating
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
    
    # Main registration form (only for the final submission)
    with st.form("register_form"):
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("Country", AFRICAN_COUNTRIES, key="country_select")
            manager = st.text_input("Manager Name", key="manager_input")
        with col2:
            rep_name = st.text_input("Representative Name", key="rep_name_input")
            rep_email = st.text_input("Email", key="rep_email_input")
            password = st.text_input("Password", type="password", key="password_input")
        
        # Submit registration
        submit_disabled = (len(squad) != 23)
        submitted = st.form_submit_button("🚀 Register Federation", use_container_width=True, disabled=submit_disabled)
        
        if submitted:
            if len(squad) == 23:
                # Final validation
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
            "status": "active" if db.federations.count_documents({}) < 7 else "waitlisted"
        }
        
        result = db.federations.insert_one(team_data)
        
        # Initialize tournament if this is the 8th team
        team_count = db.federations.count_documents({"status": "active"})
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
    """Initialize tournament bracket with 8 active teams"""
    active_teams = list(db.federations.find({"status": "active"}).limit(8))
    
    if len(active_teams) < 8:
        st.error("Not enough active teams to start tournament")
        return
    
    random.shuffle(active_teams)
    
    # Clear existing matches
    db.matches.delete_many({})
    
    # Create quarter-final matches
    for i in range(0, 8, 2):
        match_data = {
            "teamA_id": active_teams[i]["_id"],
            "teamA_name": active_teams[i]["country"],
            "teamA_rating": active_teams[i]["rating"],
            "teamB_id": active_teams[i+1]["_id"],
            "teamB_name": active_teams[i+1]["country"],
            "teamB_rating": active_teams[i+1]["rating"],
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
    
    team_count = db.federations.count_documents({"status": "active"}) if db else 0
    matches = list(db.matches.find({})) if db else []
    completed_matches = len([m for m in matches if m.get('status') == 'completed'])
    tournament = db.tournaments.find_one({}) if db else {}
    
    st.markdown(f"### Welcome back, {st.session_state.user['email']}!")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Active Teams", f"{team_count}/8")
    with col2: st.metric("Matches Played", completed_matches)
    with col3: st.metric("Tournament Status", tournament.get('status', 'pending').title())
    with col4: st.metric("Current Stage", tournament.get('current_stage', 'Not Started').title())
    
    st.markdown("---")
    
    # Display registered teams with flags
    st.subheader("🇺🇳 Tournament Teams")
    teams = list(db.federations.find({"status": "active"}).limit(8)) if db else []
    
    if teams:
        # Create columns for team display
        cols = st.columns(4)
        for i, team in enumerate(teams):
            with cols[i % 4]:
                flag = COUNTRY_FLAGS.get(team['country'], "🏴")
                st.markdown(f"""
                <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 10px; margin: 5px; text-align: center; background: linear-gradient(135deg, #f5f5f5, #e0e0e0);">
                    <h3 style="margin: 0; font-size: 1.5em;">{flag}</h3>
                    <h4 style="margin: 5px 0; color: #2E7D32;">{team['country']}</h4>
                    <p style="margin: 2px 0; font-size: 0.9em; color: #666;">Rating: {team.get('rating', 75)}</p>
                    <p style="margin: 2px 0; font-size: 0.8em; color: #888;">Manager: {team.get('manager', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No active teams in tournament.")
    
    st.markdown("---")
    
    if st.session_state.role == 'admin':
        st.subheader("🛠️ Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Start Tournament", key="home_start"):
                if db:
                    db.tournaments.update_one({}, {"$set": {"status": "active"}}, upsert=True)
                    st.success("Tournament started!")
                    st.rerun()
        with col2:
            if st.button("Reset Tournament", key="home_reset"):
                if db:
                    db.matches.delete_many({})
                    db.tournaments.delete_many({})
                    st.success("Tournament reset!")
                    st.rerun()
        with col3:
            if st.button("View All Teams", key="home_view"):
                st.session_state.current_page = "📊 Statistics"
                st.rerun()
    elif st.session_state.role == 'federation':
        user_team = db.federations.find_one({"representative_email": st.session_state.user['email']}) if db else None
        if user_team:
            flag = COUNTRY_FLAGS.get(user_team['country'], "🏴")
            st.subheader(f"{flag} Your Team: {user_team['country']}")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Rating", user_team.get('rating', 75))
            with col2: st.metric("Players", len(user_team.get('players', [])))
            with col3: st.metric("Status", user_team.get('status', 'active').title())

def show_admin():
    if st.session_state.role != 'admin':
        st.error("🔒 Admin access only")
        return
    
    st.title("👨‍💼 Admin Panel")
    db = get_database()
    
    # Tournament status
    tournament = db.tournaments.find_one({}) if db else {}
    st.subheader("Tournament Control")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Start Tournament", key="admin_start"):
            if db:
                initialize_tournament(db)
                st.success("Tournament started with quarter-finals!")
    with col2:
        if st.button("🔄 Reset Matches", key="admin_reset_matches"):
            if db:
                db.matches.delete_many({})
                st.success("All matches reset!")
    with col3:
        if st.button("🗑️ Reset All Data", key="admin_reset_all"):
            if db:
                db.matches.delete_many({})
                db.tournaments.delete_many({})
                st.success("All tournament data reset!")
    
    st.markdown("---")
    show_live_sim(db)

def show_live_sim(db):
    st.subheader("⚽ Match Simulation")
    
    if not db:
        st.error("Database not available")
        return
        
    matches = list(db.matches.find({"status": "scheduled"}))
    
    if not matches:
        st.info("No scheduled matches available")
        return
    
    match_options = []
    for match in matches:
        teamA = db.federations.find_one({"_id": match['teamA_id']})
        teamB = db.federations.find_one({"_id": match['teamB_id']})
        if teamA and teamB:
            match_options.append({
                "match": match, 
                "display": f"{teamA['country']} vs {teamB['country']}",
                "teamA_name": teamA['country'], 
                "teamB_name": teamB['country']
            })
    
    if match_options:
        selected_match_display = st.selectbox("Choose a match:", [m["display"] for m in match_options])
        selected_match_info = next((m for m in match_options if m["display"] == selected_match_display), None)
        
        if selected_match_info:
            show_match_interface(db, selected_match_info)

def show_match_interface(db, match_info):
    teamA_name, teamB_name = match_info['teamA_name'], match_info['teamB_name']
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1: st.markdown(f"### {teamA_name}")
    with col2: st.markdown("### VS")
    with col3: st.markdown(f"### {teamB_name}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎮 Play Match (AI Commentary)", use_container_width=True):
            play_match(db, match_info['match'], teamA_name, teamB_name)
    with col2:
        if st.button("⚡ Simulate Match (Quick)", use_container_width=True):
            simulate_match_quick(db, match_info['match'], teamA_name, teamB_name)

def play_match(db, match, teamA_name, teamB_name):
    st.info("🔄 Playing match with AI commentary...")
    
    try:
        # Use the enhanced match simulator with AI commentary
        score_a, score_b, goal_scorers, commentary = simulate_match_with_commentary(
            db, match["_id"], teamA_name, teamB_name
        )
        
        flag_a = COUNTRY_FLAGS.get(teamA_name, "🏴")
        flag_b = COUNTRY_FLAGS.get(teamB_name, "🏴")
        st.success(f"✅ Match completed: {flag_a} {teamA_name} {score_a}-{score_b} {teamB_name} {flag_b}")
        
        # Show match summary
        with st.expander("📝 Match Summary"):
            st.write(f"**Final Score:** {teamA_name} {score_a} - {score_b} {teamB_name}")
            if goal_scorers:
                st.write("**Goal Scorers:**")
                for goal in goal_scorers:
                    flag = COUNTRY_FLAGS.get(goal['team'], "🏴")
                    st.write(f"- {flag} {goal['player']} ({goal['minute']}')")
            
            st.write("**Match Commentary:**")
            for comment in commentary:
                st.write(f"• {comment}")
        
    except Exception as e:
        st.error(f"Error playing match: {str(e)}")
        # Fallback to basic simulation
        simulate_match_quick(db, match, teamA_name, teamB_name)
    
    st.rerun()

def simulate_match_quick(db, match, teamA_name, teamB_name):
    # Simple simulation without commentary
    score_a = random.randint(0, 3)
    score_b = random.randint(0, 3)
    
    goal_scorers = []
    for i in range(score_a):
        goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": random.randint(1, 90), "team": teamA_name})
    for i in range(score_b):
        goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": random.randint(1, 90), "team": teamB_name})
    
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
    
    # Send email notifications
    notify_federations_after_match(match["_id"])
    
    flag_a = COUNTRY_FLAGS.get(teamA_name, "🏴")
    flag_b = COUNTRY_FLAGS.get(teamB_name, "🏴")
    st.success(f"✅ Match simulated: {flag_a} {teamA_name} {score_a}-{score_b} {teamB_name} {flag_b}")
    st.rerun()

def show_federation():
    if st.session_state.role != 'federation':
        st.info("👤 Federation access only")
        return
    
    st.title("🇺🇳 My Federation")
    db = get_database()
    
    if not db:
        st.error("Database not available")
        return
        
    user_team = db.federations.find_one({"representative_email": st.session_state.user['email']})
    
    if user_team:
        flag = COUNTRY_FLAGS.get(user_team['country'], "🏴")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Team", f"{flag} {user_team['country']}")
        with col2: st.metric("Manager", user_team.get('manager', 'Unknown'))
        with col3: st.metric("Rating", user_team.get('rating', 75))
        with col4: st.metric("Status", user_team.get('status', 'active').title())
        
        st.subheader("👥 My Squad")
        
        # Group players by position
        positions = {
            "GK": "🥅 Goalkeepers",
            "DF": "🛡️ Defenders", 
            "MD": "⚡ Midfielders",
            "AT": "🎯 Attackers"
        }
        
        for pos, title in positions.items():
            position_players = [p for p in user_team.get('players', []) if p['naturalPosition'] == pos]
            if position_players:
                with st.expander(f"{title} ({len(position_players)})"):
                    for player in position_players:
                        captain = " ⭐ CAPTAIN" if player.get('isCaptain') else ""
                        rating = player['ratings'][player['naturalPosition']]
                        st.write(f"**{player['name']}** - {pos} - Rating: {rating}{captain}")
        
        # Team analytics
        st.subheader("📊 Team Analytics")
        total_players = len(user_team.get('players', []))
        if total_players > 0:
            avg_rating = user_team.get('rating', 75)
            best_position = max(["GK", "DF", "MD", "AT"], 
                              key=lambda pos: sum(p['ratings'][pos] for p in user_team.get('players', [])))
            
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Average Rating", f"{avg_rating}")
            with col2: st.metric("Squad Size", f"{total_players}/23")
            with col3: st.metric("Strongest Area", best_position)
    else:
        st.error("No team found for your account")

def show_tournament():
    st.title("🏆 Tournament Bracket")
    db = get_database()
    
    if not db:
        st.error("Database not available")
        return
        
    teams = list(db.federations.find({"status": "active"}))
    matches = list(db.matches.find({}))
    tournament = db.tournaments.find_one({}) or {}
    
    st.header("AFRICAN NATIONS LEAGUE 2025")
    st.subheader("ROAD TO THE FINAL")
    
    # Tournament status
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Status", tournament.get('status', 'Not Started').title())
    with col2: st.metric("Stage", tournament.get('current_stage', 'Quarter Finals').title())
    with col3: st.metric("Teams", len(teams))
    
    st.markdown("---")
    
    # Quarter Finals
    st.write("### 🎯 Quarter Finals")
    qf_matches = [m for m in matches if m.get('stage') == 'quarterfinal']
    
    if qf_matches:
        for match in qf_matches:
            flag_a = COUNTRY_FLAGS.get(match['teamA_name'], "🏴")
            flag_b = COUNTRY_FLAGS.get(match['teamB_name'], "🏴")
            
            if match.get('status') == 'completed':
                st.success(f"**{flag_a} {match['teamA_name']}** {match['scoreA']}-{match['scoreB']} **{match['teamB_name']} {flag_b}**")
                if match.get('method') == 'played':
                    st.caption("🎮 Played with AI Commentary")
                else:
                    st.caption("⚡ Simulated")
            else:
                st.info(f"**{flag_a} {match['teamA_name']}** vs **{match['teamB_name']} {flag_b}** - Scheduled")
    else:
        st.info("Quarter-final matches not yet generated. Admin can start the tournament.")
    
    # Show tournament progression
    completed_matches = len([m for m in matches if m.get('status') == 'completed'])
    total_matches = len(matches)
    if total_matches > 0:
        progress = completed_matches / total_matches
        st.progress(progress)
        st.write(f"Tournament Progress: {completed_matches}/{total_matches} matches completed")

def show_matches():
    st.title("⚽ Matches & Fixtures")
    db = get_database()
    
    if not db:
        st.error("Database not available")
        return
        
    matches = list(db.matches.find({}).sort("stage", 1))
    
    if not matches:
        st.info("No matches scheduled yet. Tournament needs to be started by admin.")
        return
    
    for match in matches:
        flag_a = COUNTRY_FLAGS.get(match.get('teamA_name', 'Team A'), "🏴")
        flag_b = COUNTRY_FLAGS.get(match.get('teamB_name', 'Team B'), "🏴")
        
        with st.expander(f"{match.get('stage', 'Match').title()}: {flag_a} {match.get('teamA_name', 'Team A')} vs {match.get('teamB_name', 'Team B')} {flag_b}"):
            if match.get('status') == 'completed':
                st.success(f"**Final Score: {match['scoreA']}-{match['scoreB']}**")
                st.write(f"**Method:** {match.get('method', 'unknown').title()}")
                st.write(f"**Stage:** {match.get('stage', 'Unknown').title()}")
                
                if match.get('goal_scorers'):
                    st.write("**Goal Scorers:**")
                    for goal in match['goal_scorers']:
                        flag = COUNTRY_FLAGS.get(goal['team'], "🏴")
                        st.write(f"- {flag} {goal['player']} ({goal['minute']}')")
                
                if match.get('method') == 'played' and match.get('commentary'):
                    st.write("**Match Commentary:**")
                    for comment in match['commentary'][:8]:  # Show first 8 comments
                        st.write(f"- {comment}")
                    
                    if len(match['commentary']) > 8:
                        st.write("*(Full commentary available in database)*")
            else:
                st.info("**Status:** Scheduled")
                st.write(f"**Stage:** {match.get('stage', 'Unknown').title()}")

def show_statistics():
    st.title("📊 Statistics & Analytics")
    db = get_database()
    
    if not db:
        st.error("Database not available")
        return
    
    # Team Standings with flags
    st.subheader("🏆 Team Standings")
    teams = list(db.federations.find({"status": "active"}).sort("rating", -1))
    
    if teams:
        for i, team in enumerate(teams):
            flag = COUNTRY_FLAGS.get(team['country'], "🏴")
            if i == 0:
                st.write(f"🥇 **{flag} {team['country']}** - Rating: {team.get('rating', 75)} - Manager: {team.get('manager', 'Unknown')}")
            elif i == 1:
                st.write(f"🥈 **{flag} {team['country']}** - Rating: {team.get('rating', 75)} - Manager: {team.get('manager', 'Unknown')}")
            elif i == 2:
                st.write(f"🥉 **{flag} {team['country']}** - Rating: {team.get('rating', 75)} - Manager: {team.get('manager', 'Unknown')}")
            else:
                st.write(f"**{flag} {team['country']}** - Rating: {team.get('rating', 75)} - Manager: {team.get('manager', 'Unknown')}")
    else:
        st.info("No teams registered yet")
    
    # Top Scorers
    st.subheader("🥅 Top Scorers")
    matches = list(db.matches.find({"status": "completed"}))
    all_goal_scorers = []
    
    for match in matches:
        for goal in match.get('goal_scorers', []):
            all_goal_scorers.append(goal)
    
    # Count goals by player
    goal_counts = {}
    for goal in all_goal_scorers:
        player = goal['player']
        goal_counts[player] = goal_counts.get(player, 0) + 1
    
    if goal_counts:
        sorted_scorers = sorted(goal_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (player, goals) in enumerate(sorted_scorers[:10]):
            if i == 0:
                st.write(f"🏅 **{player}** - {goals} goal{'s' if goals > 1 else ''}")
            elif i == 1:
                st.write(f"🥈 **{player}** - {goals} goal{'s' if goals > 1 else ''}")
            elif i == 2:
                st.write(f"🥉 **{player}** - {goals} goal{'s' if goals > 1 else ''}")
            else:
                st.write(f"**{player}** - {goals} goal{'s' if goals > 1 else ''}")
    else:
        st.info("No goals scored yet")
    
    # Match Statistics
    st.subheader("📈 Match Statistics")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Matches", len(matches))
    with col2: st.metric("Completed Matches", len([m for m in matches if m.get('status') == 'completed']))
    with col3: st.metric("Total Goals", len(all_goal_scorers))

if __name__ == "__main__":
    main()
