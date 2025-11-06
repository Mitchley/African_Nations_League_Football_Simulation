import streamlit as st
import random
from datetime import datetime
from frontend.utils.auth import init_session_state, login_user, logout_user
from frontend.utils.database import get_database

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
            ratings[pos] = random.randint(50, 100)
        else:
            ratings[pos] = random.randint(0, 50)
    return ratings

def calculate_team_rating(squad):
    if not squad:
        return 75.0
    total_rating = sum(p["ratings"][p["naturalPosition"]] for p in squad)
    return round(total_rating / len(squad), 2)

def get_country_flag(country):
    """Get flag emoji for each country"""
    flag_map = {
        "Algeria": "🇩🇿", "Angola": "🇦🇴", "Benin": "🇧🇯", "Botswana": "🇧🇼",
        "Burkina Faso": "🇧🇫", "Burundi": "🇧🇮", "Cameroon": "🇨🇲", "Cape Verde": "🇨🇻",
        "DR Congo": "🇨🇩", "Egypt": "🇪🇬", "Ethiopia": "🇪🇹", "Ghana": "🇬🇭",
        "Ivory Coast": "🇨🇮", "Kenya": "🇰🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿",
        "Nigeria": "🇳🇬", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "Tanzania": "🇹🇿",
        "Tunisia": "🇹🇳", "Uganda": "🇺🇬", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼"
    }
    return flag_map.get(country, "🏴")

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
    if st.button("👀 **Enter as Visitor**", use_container_width=True, type="primary"):
        st.session_state.user = {"email": "visitor@africanleague.com", "role": "visitor"}
        st.session_state.role = "visitor"
        st.success("🎉 Welcome! Entering as visitor...")
        st.rerun()

def show_federation_registration():
    st.subheader("🇺🇳 Federation Registration")
    db = get_database()
    
    existing_teams = db.federations.count_documents({})
    st.info(f"📊 Current teams in database: {existing_teams}/8")
    
    if 'squad' not in st.session_state:
        st.session_state.squad = []
    
    squad = st.session_state.squad
    
    # Player addition
    col1, col2 = st.columns([3, 1])
    with col1:
        player_name = st.text_input("Player Name", placeholder="Enter player name")
    with col2:
        pos_count = {'GK': 0, 'DF': 0, 'MD': 0, 'AT': 0}
        for player in squad:
            pos_count[player.position] += 1
        
        available_positions = []
        if pos_count['GK'] < 3: available_positions.append("GK")
        if pos_count['DF'] < 7: available_positions.append("DF")
        if pos_count['MD'] < 8: available_positions.append("MD")
        if pos_count['AT'] < 5: available_positions.append("AT")
        
        position = st.selectbox("Position", available_positions, disabled=len(available_positions) == 0)
    
    if st.button("➕ Add Player", disabled=(len(squad) >= 23 or not player_name)):
        if player_name and len(squad) < 23:
            ratings = generate_player_ratings(position)
            new_player = Player(player_name, position)
            if 'player_ratings' not in st.session_state:
                st.session_state.player_ratings = {}
            st.session_state.player_ratings[player_name] = ratings
            st.session_state.squad.append(new_player)
            st.rerun()
    
    # Squad management
    st.write(f"**Squad: {len(squad)}/23 players**")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Goalkeepers", f"{pos_count['GK']}/3")
    with col2: st.metric("Defenders", f"{pos_count['DF']}/7")
    with col3: st.metric("Midfielders", f"{pos_count['MD']}/8")
    with col4: st.metric("Attackers", f"{pos_count['AT']}/5")
    
    if squad and len(squad) == 23:
        captain_options = [f"{p.name} ({p.position})" for p in squad]
        selected_captain = st.selectbox("Select Captain", captain_options)
        captain_index = captain_options.index(selected_captain)
        for i, player in enumerate(squad):
            player.is_captain = (i == captain_index)
    
    if squad and st.button("🗑️ Clear Squad"):
        st.session_state.squad = []
        if 'player_ratings' in st.session_state:
            del st.session_state.player_ratings
        st.rerun()
    
    # Registration form
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("Country", AFRICAN_COUNTRIES)
            manager = st.text_input("Manager Name")
        with col2:
            rep_name = st.text_input("Representative Name")
            rep_email = st.text_input("Email")
            password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("🚀 Register Federation", use_container_width=True, disabled=(len(squad) != 23))
        
        if submitted and len(squad) == 23:
            if register_federation(country, manager, rep_name, rep_email, password, squad):
                st.success("✅ Registered successfully!")
                if login_user(rep_email, password):
                    st.rerun()

def register_federation(country, manager, rep_name, rep_email, password, squad):
    try:
        db = get_database()
        
        if db.users.find_one({"email": rep_email}):
            st.error("❌ Email already registered")
            return False
        
        if db.federations.find_one({"country": country}):
            st.error("❌ Country already registered")
            return False
        
        db.users.insert_one({
            "email": rep_email, "password": password, "role": "federation", 
            "country": country, "created_at": datetime.now()
        })
        
        team_rating = calculate_team_rating(squad)
        
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
    teams = list(db.federations.find({}))
    random.shuffle(teams)
    
    db.matches.delete_many({})
    
    # Schedule quarter finals for all 8 teams
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
    
    tournament_data = {
        "status": "active",
        "current_stage": "quarterfinal",
        "created_at": datetime.now()
    }
    db.tournaments.update_one({}, {"$set": tournament_data}, upsert=True)

def advance_tournament(db):
    """Advance tournament to next stage when matches are completed"""
    # Check if all quarter finals are completed
    quarter_finals = list(db.matches.find({"stage": "quarterfinal"}))
    if all(match.get('status') == 'completed' for match in quarter_finals):
        # Create semi finals
        winners = []
        for match in quarter_finals:
            if match['scoreA'] > match['scoreB']:
                winners.append({"id": match['teamA_id'], "name": match['teamA_name']})
            else:
                winners.append({"id": match['teamB_id'], "name": match['teamB_name']})
        
        # Create semi final matches
        for i in range(0, 4, 2):
            match_data = {
                "teamA_id": winners[i]["id"],
                "teamA_name": winners[i]["name"],
                "teamB_id": winners[i+1]["id"],
                "teamB_name": winners[i+1]["name"],
                "stage": "semifinal",
                "status": "scheduled",
                "scoreA": 0,
                "scoreB": 0,
                "goal_scorers": [],
                "commentary": [],
                "method": "not_played",
                "created_at": datetime.now()
            }
            db.matches.insert_one(match_data)
        
        db.tournaments.update_one({}, {"$set": {"current_stage": "semifinal"}})
    
    # Check if all semi finals are completed
    semi_finals = list(db.matches.find({"stage": "semifinal"}))
    if all(match.get('status') == 'completed' for match in semi_finals):
        # Create final
        winners = []
        for match in semi_finals:
            if match['scoreA'] > match['scoreB']:
                winners.append({"id": match['teamA_id'], "name": match['teamA_name']})
            else:
                winners.append({"id": match['teamB_id'], "name": match['teamB_name']})
        
        # Create final match
        match_data = {
            "teamA_id": winners[0]["id"],
            "teamA_name": winners[0]["name"],
            "teamB_id": winners[1]["id"],
            "teamB_name": winners[1]["name"],
            "stage": "final",
            "status": "scheduled",
            "scoreA": 0,
            "scoreB": 0,
            "goal_scorers": [],
            "commentary": [],
            "method": "not_played",
            "created_at": datetime.now()
        }
        db.matches.insert_one(match_data)
        
        db.tournaments.update_one({}, {"$set": {"current_stage": "final"}})

def show_app():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    with st.sidebar:
        if st.session_state.role == "visitor":
            st.markdown("### 👋 Welcome, Visitor!")
            pages = ["🏠 Home", "🏆 Tournament", "📊 Statistics"]
        else:
            st.markdown(f"### 👋 Welcome, {st.session_state.user['email']}!")
            if st.session_state.role == "admin":
                pages = ["🏠 Home", "👨‍💼 Admin", "🏆 Tournament", "⚽ Matches", "📊 Statistics"]
            else:
                pages = ["🏠 Home", "🇺🇳 Federation", "🏆 Tournament", "⚽ Matches", "📊 Statistics"]
        
        st.markdown("---")
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
    
    teams = list(db.federations.find({}))
    matches = list(db.matches.find({}))
    tournament = db.tournaments.find_one({}) or {}
    
    st.markdown(f"### Welcome back, {st.session_state.user['email']}!")
    
    # Overview Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("Total Teams", len(teams))
    with col2:
        completed_matches = len([m for m in matches if m.get('status') == 'completed'])
        st.metric("Matches Played", completed_matches)
    with col3:
        total_matches = len(matches)
        st.metric("Total Matches", total_matches)
    with col4:
        status = tournament.get('status', 'pending').title()
        st.metric("Tournament Status", status)
    
    st.markdown("---")
    
    # Updated tabs - changed "Fixtures" to "Tournament Progress"
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Teams", "📈 Tournament Progress", "📊 Standings", "🎯 Top Scorers"])
    
    with tab1:
        show_teams_section(teams)
    
    with tab2:
        show_tournament_progress_section(matches, db)
    
    with tab3:
        show_standings_section(teams)
    
    with tab4:
        show_top_scorers_section(matches)

def show_teams_section(teams):
    st.subheader("Registered Teams")
    if not teams:
        st.info("No teams registered yet")
        return
    
    # Display teams with flags only
    cols = st.columns(4)  # 4 columns for better layout
    for i, team in enumerate(teams):
        with cols[i % 4]:
            flag = get_country_flag(team['country'])
            st.markdown(f"""
            <div style='border: 2px solid #1e3c72; border-radius: 10px; padding: 20px; margin: 10px 0; background: #f8f9fa; text-align: center;'>
                <h3 style='margin:0; color: #1e3c72;'>{flag} {team['country']}</h3>
            </div>
            """, unsafe_allow_html=True)

def show_tournament_progress_section(matches, db):
    st.subheader("Tournament Progress")
    if not matches:
        st.info("No matches scheduled yet")
        return
    
    # Group matches by stage
    rounds = {}
    for match in matches:
        round_name = match.get('stage', 'quarterfinal')
        if round_name not in rounds:
            rounds[round_name] = []
        rounds[round_name].append(match)
    
    # Define the order of tournament stages
    stage_order = ["quarterfinal", "semifinal", "final"]
    
    # Display matches in tournament stage order
    for stage in stage_order:
        if stage in rounds:
            stage_matches = rounds[stage]
            
            # Format stage name for display
            if stage == "quarterfinal":
                stage_display_name = "Quarter Finals"
            elif stage == "semifinal":
                stage_display_name = "Semi Finals"
            elif stage == "final":
                stage_display_name = "Final"
            else:
                stage_display_name = stage.title()
            
            st.markdown(f"### {stage_display_name}")
            
            for i, match in enumerate(stage_matches):
                teamA_name = match.get('teamA_name', 'TBD')
                teamB_name = match.get('teamB_name', 'TBD')
                
                # Create a container for each match with better styling
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 3, 2])
                    with col1: 
                        flag_a = get_country_flag(teamA_name)
                        st.write(f"**{flag_a} {teamA_name}**")
                    with col2:
                        if match.get('status') == 'completed':
                            st.write(f"**{match.get('scoreA', 0)} - {match.get('scoreB', 0)}**")
                        else:
                            st.write("**VS**")
                    with col3: 
                        flag_b = get_country_flag(teamB_name)
                        st.write(f"**{flag_b} {teamB_name}**")
                    with col4:
                        if match.get('status') == 'completed':
                            st.success(f"✅ Completed")
                            # Show goal scorers in expander for completed matches
                            if match.get('goal_scorers'):
                                with st.expander("Goal Scorers"):
                                    for goal in match['goal_scorers']:
                                        st.write(f"⚽ {goal['player']} ({goal['minute']}') - {goal['team']}")
                        else:
                            st.info("🕐 Scheduled")
                
                # Add a subtle divider between matches
                if i < len(stage_matches) - 1:
                    st.markdown("<hr style='margin: 10px 0; border: 0.5px solid #f0f0f0;'>", unsafe_allow_html=True)

def show_standings_section(teams):
    st.subheader("Team Standings")
    if not teams:
        st.info("No teams registered yet")
        return
    
    sorted_teams = sorted(teams, key=lambda x: x.get('points', 0), reverse=True)
    
    for i, team in enumerate(sorted_teams):
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        with col1:
            if i == 0: st.write("🥇")
            elif i == 1: st.write("🥈")
            elif i == 2: st.write("🥉")
            else: st.write(f"#{i+1}")
        with col2: 
            flag = get_country_flag(team['country'])
            st.write(f"**{flag} {team['country']}**")
        with col3: st.write(f"**{team.get('points', 0)}** pts")
        with col4: st.write(f"Rating: {team.get('rating', 75)}")

def show_top_scorers_section(matches):
    st.subheader("Top Scorers")
    all_goal_scorers = []
    for match in matches:
        if match.get('status') == 'completed' and match.get('goal_scorers'):
            all_goal_scorers.extend(match['goal_scorers'])
    
    if not all_goal_scorers:
        st.info("No goals scored yet in the tournament")
        return
    
    goal_counts = {}
    for goal in all_goal_scorers:
        player = goal['player']
        goal_counts[player] = goal_counts.get(player, 0) + 1
    
    sorted_scorers = sorted(goal_counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (player, goals) in enumerate(sorted_scorers[:10]):
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if i == 0: st.write("👑")
            elif i == 1: st.write("🥈")
            elif i == 2: st.write("🥉")
            else: st.write(f"#{i+1}")
        with col2: st.write(f"**{player}**")
        with col3: st.write(f"**{goals}** goal{'s' if goals > 1 else ''}")

def show_admin():
    if st.session_state.role != 'admin':
        st.error("🔒 Admin access only")
        return
    
    st.title("👨‍💼 Admin Panel")
    db = get_database()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Tournament"):
            db.tournaments.update_one({}, {"$set": {"status": "active"}}, upsert=True)
            st.success("Started!")
    with col2:
        if st.button("🔄 Reset Tournament"):
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
            teamA_name, teamB_name = selected_match_info['teamA_name'], selected_match_info['teamB_name']
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1: 
                flag_a = get_country_flag(teamA_name)
                st.markdown(f"### {flag_a} {teamA_name}")
            with col2: st.markdown("### VS")
            with col3: 
                flag_b = get_country_flag(teamB_name)
                st.markdown(f"### {flag_b} {teamB_name}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎮 Play Match", use_container_width=True):
                    play_match(db, selected_match_info['match'], teamA_name, teamB_name)
                    advance_tournament(db)  # Check if we can advance tournament
            with col2:
                if st.button("⚡ Simulate Match", use_container_width=True):
                    simulate_match_quick(db, selected_match_info['match'], teamA_name, teamB_name)
                    advance_tournament(db)  # Check if we can advance tournament

def play_match(db, match, teamA_name, teamB_name):
    st.info("🔄 Playing match with commentary...")
    
    commentary = [f"Match between {teamA_name} and {teamB_name} kicks off!"]
    score_a, score_b = 0, 0
    goal_scorers = []
    
    for minute in range(1, 91):
        if random.random() < 0.05:
            if random.random() < 0.5:
                score_a += 1
                commentary.append(f"{minute}' - GOAL! {teamA_name} scores!")
                goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": minute, "team": teamA_name})
            else:
                score_b += 1
                commentary.append(f"{minute}' - GOAL! {teamB_name} scores!")
                goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": minute, "team": teamB_name})
        elif random.random() < 0.08:
            events = ["Great save!", "Corner kick", "Yellow card", "Close chance!"]
            commentary.append(f"{minute}' - {random.choice(events)}")
    
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
        with col1: 
            flag = get_country_flag(user_team['country'])
            st.metric("Team", f"{flag} {user_team['country']}")
        with col2: st.metric("Manager", user_team.get('manager', 'Unknown'))
        with col3: st.metric("Rating", user_team.get('rating', 75))
        
        st.subheader("👥 My Squad")
        for player in user_team.get('players', []):
            captain = " ⭐" if player.get('isCaptain') else ""
            rating = player['ratings'][player['naturalPosition']]
            st.write(f"• {player['name']} ({player['naturalPosition']}) - Rating: {rating}{captain}")

def show_tournament():
    st.title("🏆 Tournament Bracket")
    db = get_database()
    
    teams = list(db.federations.find({}))
    matches = list(db.matches.find({}))
    
    st.header("AFRICAN NATIONS LEAGUE 2025")
    st.subheader("ROAD TO THE FINAL")
    
    # Show all tournament stages
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown("### 🏁 Quarter Finals")
        qf_matches = [m for m in matches if m.get('stage') == 'quarterfinal']
        for i, match in enumerate(qf_matches):
            display_match_card(match, f"Match {i+1}")
    
    with col2:
        st.markdown("### ⬆️ Semi Finals")
        sf_matches = [m for m in matches if m.get('stage') == 'semifinal']
        if sf_matches:
            for i, match in enumerate(sf_matches):
                display_match_card(match, f"SF {i+1}")
        else:
            st.write("**SF 1:**")
            st.write("👑 Winner QF 1")
            st.write("👑 Winner QF 2")
            st.write("**SF 2:**")
            st.write("👑 Winner QF 3")
            st.write("👑 Winner QF 4")
    
    with col3:
        st.markdown("### 🏆 Final")
        final_matches = [m for m in matches if m.get('stage') == 'final']
        if final_matches:
            for match in final_matches:
                display_match_card(match, "Final")
        else:
            st.write("⭐ Winner SF 1")
            st.write("⭐ Winner SF 2")

def display_match_card(match, title=""):
    if title:
        st.write(f"**{title}:**")
    
    teamA_name = match.get('teamA_name', 'Team A')
    teamB_name = match.get('teamB_name', 'Team B')
    
    if match.get('status') == 'completed':
        score_a = match.get('scoreA', 0)
        score_b = match.get('scoreB', 0)
        col1, col2, col3 = st.columns([3, 1, 3])
        with col1: 
            flag_a = get_country_flag(teamA_name)
            st.write(f"**{flag_a} {teamA_name}**")
        with col2: st.write(f"**{score_a}-{score_b}**")
        with col3: 
            flag_b = get_country_flag(teamB_name)
            st.write(f"**{flag_b} {teamB_name}**")
    else:
        col1, col2, col3 = st.columns([3, 1, 3])
        with col1: 
            flag_a = get_country_flag(teamA_name)
            st.write(f"**{flag_a} {teamA_name}**")
        with col2: st.write("**VS**")
        with col3: 
            flag_b = get_country_flag(teamB_name)
            st.write(f"**{flag_b} {teamB_name}**")

def show_matches():
    st.title("⚽ Matches & Fixtures")
    db = get_database()
    
    matches = list(db.matches.find({}))
    
    for match in matches:
        teamA_name = match.get('teamA_name', 'Team A')
        teamB_name = match.get('teamB_name', 'Team B')
        flag_a = get_country_flag(teamA_name)
        flag_b = get_country_flag(teamB_name)
        
        with st.expander(f"{flag_a} {teamA_name} vs {flag_b} {teamB_name}"):
            if match.get('status') == 'completed':
                st.success(f"**Final Score: {match['scoreA']}-{match['scoreB']}**")
                if match.get('goal_scorers'):
                    st.write("**Goal Scorers:**")
                    for goal in match['goal_scorers']:
                        st.write(f"- {goal['player']} ({goal['minute']}')")
            else:
                st.info("**Status:** Scheduled")

def show_statistics():
    st.title("📊 Statistics")
    db = get_database()
    
    # Team Standings
    st.subheader("🏆 Team Standings")
    teams = list(db.federations.find({}).sort("points", -1))
    
    if teams:
        for i, team in enumerate(teams):
            col1, col2, col3 = st.columns([1, 3, 2])
            with col1: st.write(f"**#{i+1}**")
            with col2: 
                flag = get_country_flag(team['country'])
                st.write(f"**{flag} {team['country']}**")
            with col3: st.write(f"Points: **{team.get('points', 0)}**")
    
    st.markdown("---")
    
    # Top Scorers
    st.subheader("🥅
