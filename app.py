import streamlit as st
import time
import random
from datetime import datetime
from frontend.utils.auth import init_session_state, login_user, logout_user
from frontend.utils.database import save_team, get_database, get_players_by_federation
from frontend.utils.match_simulator import simulate_match

init_session_state()

AFRICAN_COUNTRIES = ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", "DR Congo", "Egypt", "Ethiopia", "Ghana", "Ivory Coast", "Kenya", "Morocco", "Mozambique", "Nigeria", "Senegal", "South Africa", "Tanzania", "Tunisia", "Uganda", "Zambia", "Zimbabwe"]

AFRICAN_FIRST_NAMES = ["Mohamed", "Youssef", "Ahmed", "Kofi", "Kwame", "Adebayo", "Tendai", "Blessing", "Ibrahim", "Abdul", "Chinedu", "Faith"]
AFRICAN_LAST_NAMES = ["Diallo", "Traore", "Mensah", "Adebayo", "Okafor", "Mohammed", "Ibrahim", "Kamara", "Sow", "Keita", "Ndiaye", "Conte"]

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

def auto_generate_squad():
    positions = ["GK"] * 3 + ["DF"] * 7 + ["MD"] * 8 + ["AT"] * 5
    squad = []
    
    for pos in positions:
        ratings = generate_player_ratings(pos)
        squad.append({
            "name": generate_player_name(),
            "naturalPosition": pos,
            "ratings": ratings,
            "isCaptain": False
        })
    
    # Select captain from outfield players
    outfield_players = [p for p in squad if p["naturalPosition"] != "GK"]
    if outfield_players:
        random.choice(outfield_players)["isCaptain"] = True
    
    return squad

def calculate_team_rating(squad):
    if not squad:
        return 75.0
    total_rating = sum(p["ratings"][p["naturalPosition"]] for p in squad)
    return round(total_rating / len(squad), 2)

def main():
    st.set_page_config(page_title="African Nations League", layout="wide", page_icon="⚽")
    
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
        <h1 style="margin:0; color: #FFD700;">🏆 AFRICAN NATIONS LEAGUE</h1>
        <p style="margin:0;">Road to Glory 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 **Admin Login**", "🇺🇳 **Federation Sign Up**", "👤 **Visitor Access**"])
    
    with tab1: show_admin_login()
    with tab2: show_federation_registration()
    with tab3: show_visitor_access()

def show_admin_login():
    st.subheader("Admin Login")
    st.info("Use admin credentials to access tournament management")
    
    with st.form("admin_login_form"):
        email = st.text_input("**Email**", placeholder="admin@africanleague.com")
        password = st.text_input("**Password**", type="password")
        
        if st.form_submit_button("🚀 **Login as Admin**", use_container_width=True):
            if email and password and login_user(email, password):
                st.success("✅ Admin login successful!")
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
        st.rerun()

def show_federation_registration():
    st.subheader("🇺🇳 Federation Registration")
    
    db = get_database()
    
    # Check current team count
    existing_teams = db.federations.count_documents({})
    is_eighth_team = existing_teams == 7
    
    st.info(f"📊 Current teams in database: {existing_teams}/8")
    
    if is_eighth_team:
        st.success("🎉 You're registering the 8th team! Tournament will start after registration.")
    
    # Use a separate form for adding players
    col1, col2 = st.columns([3, 1])
    with col1:
        player_name = st.text_input("Player Name", placeholder="Enter player name", key="player_name_input")
    with col2:
        # Calculate current position counts
        if 'squad' not in st.session_state:
            st.session_state.squad = []
        
        squad = st.session_state.squad
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
    
    # Add player button (outside the main form)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        add_disabled = (len(squad) >= 23 or not player_name or len(available_positions) == 0)
        if st.button("➕ Add Player", disabled=add_disabled, use_container_width=True):
            if player_name and len(squad) < 23:
                # Generate ratings according to requirements
                ratings = {}
                for pos in ["GK", "DF", "MD", "AT"]:
                    if pos == position:
                        ratings[pos] = random.randint(50, 100)  # Natural position: 50-100
                    else:
                        ratings[pos] = random.randint(0, 50)    # Non-natural: 0-50
                
                # Create Player object
                new_player = Player(player_name, position)
                # Store ratings in session state
                if 'player_ratings' not in st.session_state:
                    st.session_state.player_ratings = {}
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
                        if 'player_ratings' in st.session_state:
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
        db.users.insert_one({
            "email": rep_email, "password": password, "role": "federation", 
            "country": country, "created_at": datetime.now()
        })
        
        # Calculate team rating
        team_rating = calculate_team_rating(squad)
        
        # Save team
        team_data = {
            "country": country, 
            "manager": manager, 
            "representative_name": rep_name,
            "representative_email": rep_email, 
            "rating": team_rating, 
            "players": squad,
            "points": 0, 
            "registered_at": datetime.now()
        }
        
        db.federations.insert_one(team_data)
        
        # Initialize tournament if 8 teams
        team_count = db.federations.count_documents({})
        if team_count >= 8:
            initialize_tournament(db)
            st.balloons()
            st.success("🎊 Tournament started with 8 teams!")
        
        if 'squad' in st.session_state:
            del st.session_state.squad
            
        return True
        
    except Exception as e:
        st.error(f"❌ Registration error: {str(e)}")
        return False

def initialize_tournament(db):
    """Initialize tournament bracket with 8 teams"""
    teams = list(db.federations.find({}))
    random.shuffle(teams)
    
    # Clear existing matches
    db.matches.delete_many({})
    
    # Create quarter-final matches
    for i in range(0, 8, 2):
        match_data = {
            "teamA_id": teams[i]["_id"],
            "teamA_name": teams[i]["country"],
            "teamB_id": teams[i+1]["_id"],
            "teamB_name": teams[i+1]["country"],
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
        "created_at": datetime.now()
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
    st.title("🏠 African Nations League")
    db = get_database()
    
    team_count = db.federations.count_documents({})
    matches = list(db.matches.find({}))
    completed_matches = len([m for m in matches if m.get('status') == 'completed'])
    tournament = db.tournaments.find_one({}) or {}
    
    st.markdown(f"### Welcome back, {st.session_state.user['email']}!")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Teams", f"{team_count}/8")
    with col2: st.metric("Matches Played", completed_matches)
    with col3: st.metric("Status", tournament.get('status', 'pending').title())
    
    st.markdown("---")
    
    if st.session_state.role == 'admin':
        st.subheader("🛠️ Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Tournament", key="home_start"):
                db.tournaments.update_one({}, {"$set": {"status": "active"}}, upsert=True)
                st.success("Tournament started!")
                st.rerun()
    elif st.session_state.role == 'federation':
        user_team = db.federations.find_one({"representative_email": st.session_state.user['email']})
        if user_team:
            st.subheader(f"🇺🇳 Your Team: {user_team['country']}")
            col1, col2 = st.columns(2)
            with col1: st.metric("Rating", user_team.get('rating', 75))
            with col2: st.metric("Players", len(user_team.get('players', [])))

def show_admin():
    if st.session_state.role != 'admin':
        st.error("🔒 Admin access only")
        return
    
    st.title("👨‍💼 Admin Panel")
    db = get_database()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Tournament", key="admin_start"):
            db.tournaments.update_one({}, {"$set": {"status": "active"}}, upsert=True)
            st.success("Started!")
    with col2:
        if st.button("🔄 Reset Tournament", key="admin_reset"):
            db.matches.delete_many({})
            db.tournaments.delete_many({})
            st.success("Tournament reset!")
    
    st.markdown("---")
    show_live_sim(db)

def show_live_sim(db):
    st.subheader("⚽ Match Simulation")
    
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
        if st.button("🎮 Play Match", use_container_width=True):
            play_match(db, match_info['match'], teamA_name, teamB_name)
    with col2:
        if st.button("⚡ Simulate Match", use_container_width=True):
            simulate_match_quick(db, match_info['match'], teamA_name, teamB_name)

def play_match(db, match, teamA_name, teamB_name):
    st.info("🔄 Playing match with commentary...")
    
    # Simulate match with commentary
    commentary = [f"Match between {teamA_name} and {teamB_name} kicks off!"]
    score_a, score_b = 0, 0
    goal_scorers = []
    
    for minute in range(1, 91):
        # Chance for events
        if random.random() < 0.05:  # 5% chance per minute for goal
            if random.random() < 0.5:
                score_a += 1
                commentary.append(f"{minute}' - GOAL! {teamA_name} scores!")
                goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": minute, "team": teamA_name})
            else:
                score_b += 1
                commentary.append(f"{minute}' - GOAL! {teamB_name} scores!")
                goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": minute, "team": teamB_name})
        elif random.random() < 0.08:  # Other match events
            events = ["Great save!", "Corner kick", "Yellow card", "Close chance!"]
            commentary.append(f"{minute}' - {random.choice(events)}")
    
    # Update match in database
    db.matches.update_one(
        {"_id": match["_id"]},
        {"$set": {
            "status": "completed",
            "scoreA": score_a,
            "scoreB": score_b,
            "goal_scorers": goal_scorers,
            "commentary": commentary,
            "method": "played"
        }}
    )
    
    st.success(f"✅ Match completed: {teamA_name} {score_a}-{score_b} {teamB_name}")
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
    
    st.success(f"✅ Match simulated: {teamA_name} {score_a}-{score_b} {teamB_name}")
    st.rerun()

def show_federation():
    if st.session_state.role != 'federation':
        st.info("👤 Federation access only")
        return
    
    st.title("🇺🇳 My Federation")
    db = get_database()
    
    user_team = db.federations.find_one({"representative_email": st.session_state.user['email']})
    
    if user_team:
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Team", user_team['country'])
        with col2: st.metric("Manager", user_team.get('manager', 'Unknown'))
        with col3: st.metric("Rating", user_team.get('rating', 75))
        
        st.subheader("👥 My Squad")
        for player in user_team.get('players', []):
            captain = " ⭐" if player.get('isCaptain') else ""
            rating = player['ratings'][player['naturalPosition']]
            st.write(f"• {player['name']} ({player['naturalPosition']}) - Rating: {rating}{captain}")
    else:
        st.error("No team found for your account")

def show_tournament():
    st.title("🏆 Tournament Bracket")
    db = get_database()
    
    teams = list(db.federations.find({}))
    matches = list(db.matches.find({}))
    
    st.header("AFRICAN NATIONS LEAGUE 2025")
    st.subheader("ROAD TO THE FINAL")
    
    # Quarter Finals
    st.write("### Quarter Finals")
    qf_matches = [m for m in matches if m.get('stage') == 'quarterfinal']
    
    for match in qf_matches:
        if match.get('status') == 'completed':
            st.success(f"**{match['teamA_name']}** {match['scoreA']}-{match['scoreB']} **{match['teamB_name']}**")
        else:
            st.info(f"**{match['teamA_name']}** vs **{match['teamB_name']}** - Scheduled")
    
    # Show teams if no matches yet
    if not qf_matches and teams:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Left Bracket**")
            for team in teams[:4]:
                st.write(f"• {team['country']}")
        with col2:
            st.write("**Right Bracket**")
            for team in teams[4:8]:
                st.write(f"• {team['country']}")

def show_matches():
    st.title("⚽ Matches & Fixtures")
    db = get_database()
    
    matches = list(db.matches.find({}))
    
    for match in matches:
        with st.expander(f"{match.get('teamA_name', 'Team A')} vs {match.get('teamB_name', 'Team B')}"):
            if match.get('status') == 'completed':
                st.success(f"**Final Score: {match['scoreA']}-{match['scoreB']}**")
                st.write(f"**Method:** {match.get('method', 'unknown').title()}")
                
                if match.get('goal_scorers'):
                    st.write("**Goal Scorers:**")
                    for goal in match['goal_scorers']:
                        st.write(f"- {goal['player']} ({goal['minute']}')")
                
                if match.get('method') == 'played' and match.get('commentary'):
                    st.write("**Match Commentary:**")
                    for comment in match['commentary'][:5]:  # Show first 5 comments
                        st.write(f"- {comment}")
            else:
                st.info("**Status:** Scheduled")

def show_statistics():
    st.title("📊 Statistics")
    db = get_database()
    
    # Team Standings
    st.subheader("🏆 Team Standings")
    teams = list(db.federations.find({}))
    for team in teams:
        st.write(f"**{team['country']}** - Rating: {team.get('rating', 75)}")
    
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
    
    for player, goals in sorted(goal_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        st.write(f"**{player}** - {goals} goals")

if __name__ == "__main__":
    main()
