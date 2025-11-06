import streamlit as st
import random
from datetime import datetime
from bson import ObjectId
from frontend.utils.auth import init_session_state, login_user, logout_user
from frontend.utils.database import get_database
from backend.utils.match_simulator import MatchSimulator
from backend.email_service import EmailService

# Initialize services
match_simulator = MatchSimulator()
email_service = EmailService()

init_session_state()

AFRICAN_COUNTRIES = ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", "DR Congo", "Egypt", "Ethiopia", "Ghana", "Ivory Coast", "Kenya", "Morocco", "Mozambique", "Nigeria", "Senegal", "South Africa", "Tanzania", "Tunisia", "Uganda", "Zambia", "Zimbabwe"]
AFRICAN_FIRST_NAMES = ["Mohamed", "Youssef", "Ahmed", "Kofi", "Kwame", "Adebayo", "Tendai", "Blessing", "Ibrahim", "Abdul", "Chinedu", "Faith"]
AFRICAN_LAST_NAMES = ["Diallo", "Traore", "Mensah", "Adebayo", "Okafor", "Mohammed", "Ibrahim", "Kamara", "Sow", "Keita", "Ndiaye", "Conte"]
COUNTRY_FLAGS = {country: "🇩🇿🇦🇴🇧🇯🇧🇼🇧🇫🇧🇮🇨🇲🇨🇻🇨🇩🇪🇬🇪🇹🇬🇭🇨🇮🇰🇪🇲🇦🇲🇿🇳🇬🇸🇳🇿🇦🇹🇿🇹🇳🇺🇬🇿🇲🇿🇼"[i*2:i*2+2] for i, country in enumerate(AFRICAN_COUNTRIES)}

class Player:
    def __init__(self, name, position, is_captain=False):
        self.name = name
        self.position = position
        self.is_captain = is_captain

def generate_player_name():
    return f"{random.choice(AFRICAN_FIRST_NAMES)} {random.choice(AFRICAN_LAST_NAMES)}"

def generate_player_ratings(position):
    return {pos: random.randint(50, 100) if pos == position else random.randint(0, 50) 
            for pos in ["GK", "DF", "MD", "AT"]}

def calculate_team_rating(squad):
    return round(sum(p["ratings"][p["naturalPosition"]] for p in squad) / len(squad), 2) if squad else 75.0

def get_country_flag(country):
    return COUNTRY_FLAGS.get(country, "🏴")

def safe_objectid_conversion(obj_id):
    if isinstance(obj_id, ObjectId):
        return obj_id
    try:
        return ObjectId(obj_id)
    except:
        return obj_id

def send_match_notifications(db, match_data):
    """Send email notifications to both teams"""
    try:
        # Get team emails
        team_a = db.federations.find_one({"_id": safe_objectid_conversion(match_data['teamA_id'])})
        team_b = db.federations.find_one({"_id": safe_objectid_conversion(match_data['teamB_id'])})
        
        if team_a and team_b:
            email_data = {
                'teamA': match_data['teamA_name'],
                'teamB': match_data['teamB_name'],
                'scoreA': match_data['scoreA'],
                'scoreB': match_data['scoreB'],
                'stage': match_data['stage'],
                'status': 'completed',
                'goal_scorers': match_data.get('goal_scorers', [])
            }
            
            # Send to team A
            email_service.send_match_result(team_a['representative_email'], email_data)
            # Send to team B
            email_service.send_match_result(team_b['representative_email'], email_data)
            
            st.success("📧 Match notifications sent to both teams!")
            
    except Exception as e:
        st.error(f"Failed to send notifications: {e}")

def main():
    st.set_page_config(page_title="African Nations League", layout="wide", page_icon="⚽")
    if not st.session_state.user:
        hide_sidebar()
        show_login_page()
    else:
        show_app()

def hide_sidebar():
    st.markdown("""<style>section[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)

def show_login_page():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e3c72 0%,#2a5298 100%);padding:3rem;border-radius:20px;color:white;text-align:center;margin-bottom:2rem;border:4px solid #FFD700;">
        <h1 style="margin:0;color:#FFD700;">🏆 AFRICAN NATIONS LEAGUE</h1><p style="margin:0;">Road to Glory 2025</p>
    </div>""", unsafe_allow_html=True)
    
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
        
        available_positions = [pos for pos in ["GK", "DF", "MD", "AT"] 
                             if pos_count[pos] < (3 if pos == "GK" else 7 if pos == "DF" else 8 if pos == "MD" else 5)]
        position = st.selectbox("Position", available_positions, disabled=not available_positions)
    
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
        
        # Convert squad to dictionary format for storage
        squad_dicts = []
        for player in squad:
            player_dict = {
                "name": player.name,
                "naturalPosition": player.position,
                "isCaptain": player.is_captain,
                "ratings": st.session_state.player_ratings.get(player.name, generate_player_ratings(player.position))
            }
            squad_dicts.append(player_dict)
        
        db.users.insert_one({
            "email": rep_email, "password": password, "role": "federation", 
            "country": country, "created_at": datetime.now()
        })
        
        team_rating = calculate_team_rating(squad_dicts)
        team_data = {
            "country": country, "manager": manager, "representative_name": rep_name,
            "representative_email": rep_email, "rating": team_rating, "players": squad_dicts,
            "points": 0, "registered_at": datetime.now()
        }
        db.federations.insert_one(team_data)
        
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
    teams = list(db.federations.find({}))
    random.shuffle(teams)
    db.matches.delete_many({})
    
    for i in range(0, 8, 2):
        match_data = {
            "teamA_id": teams[i]["_id"], "teamA_name": teams[i]["country"],
            "teamB_id": teams[i+1]["_id"], "teamB_name": teams[i+1]["country"],
            "stage": "quarterfinal", "status": "scheduled", "scoreA": 0, "scoreB": 0,
            "goal_scorers": [], "commentary": [], "method": "not_played", "created_at": datetime.now()
        }
        db.matches.insert_one(match_data)
    
    tournament_data = {"status": "active", "current_stage": "quarterfinal", "created_at": datetime.now()}
    db.tournaments.update_one({}, {"$set": tournament_data}, upsert=True)

def show_app():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    with st.sidebar:
        if st.session_state.role == "visitor":
            st.markdown("### 👋 Welcome, Visitor!")
            pages = ["🏠 Home", "🏆 Tournament", "📊 Statistics"]
        else:
            st.markdown(f"### 👋 Welcome, {st.session_state.user['email']}!")
            pages = ["🏠 Home", "👨‍💼 Admin", "🏆 Tournament", "📈 Tournament Progress", "📊 Statistics"] if st.session_state.role == "admin" else ["🏠 Home", "🇺🇳 Federation", "🏆 Tournament", "📈 Tournament Progress", "📊 Statistics"]
        
        st.markdown("---")
        for page in pages:
            if st.button(page, use_container_width=True, type="primary" if st.session_state.current_page == page else "secondary"):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    show_current_page()

def show_current_page():
    page_mapping = {
        "🏠 Home": show_home, "👨‍💼 Admin": show_admin, "🇺🇳 Federation": show_federation,
        "🏆 Tournament": show_tournament, "📈 Tournament Progress": show_tournament_progress, "📊 Statistics": show_statistics
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
    with col1: st.metric("Total Teams", len(teams))
    with col2: st.metric("Matches Played", len([m for m in matches if m.get('status') == 'completed']))
    with col3: st.metric("Total Matches", len(matches))
    with col4: st.metric("Tournament Status", tournament.get('status', 'pending').title())
    
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Teams", "📈 Tournament Progress", "📊 Standings", "🎯 Top Scorers"])
    with tab1: show_teams_section(teams)
    with tab2: show_tournament_progress_section(matches, db)
    with tab3: show_standings_section(teams)
    with tab4: show_top_scorers_section(matches)

def show_teams_section(teams):
    st.subheader("Registered Teams")
    if not teams:
        st.info("No teams registered yet")
        return
    
    cols = st.columns(3)
    for i, team in enumerate(teams):
        with cols[i % 3]:
            flag = get_country_flag(team['country'])
            st.markdown(f"""
            <div style='border:2px solid #1e3c72;border-radius:10px;padding:15px;margin:10px 0;background:#f8f9fa;'>
                <h4 style='margin:0;color:#1e3c72;'>{flag} {team['country']}</h4>
                <p style='margin:5px 0;'><strong>Manager:</strong> {team.get('manager','Unknown')}</p>
                <p style='margin:5px 0;'><strong>Rating:</strong> {team.get('rating',75)}</p>
                <p style='margin:5px 0;'><strong>Points:</strong> {team.get('points',0)}</p>
            </div>""", unsafe_allow_html=True)

def show_tournament_progress_section(matches, db):
    st.subheader("Tournament Progress")
    if not matches:
        st.info("No matches scheduled yet")
        return
    
    # Get tournament stage
    tournament = db.tournaments.find_one({}) or {}
    current_stage = tournament.get('current_stage', 'quarterfinal')
    
    st.info(f"**Current Stage: {current_stage.upper()}**")
    
    rounds = {}
    for match in matches:
        round_name = match.get('stage', 'unknown')
        if round_name not in rounds:
            rounds[round_name] = []
        rounds[round_name].append(match)
    
    # Display matches by stage in order
    stages_order = ['quarterfinal', 'semifinal', 'final']
    for stage in stages_order:
        if stage in rounds:
            st.markdown(f"### {stage.upper().replace('FINAL', 'FINALS')}")
            for match in rounds[stage]:
                teamA_name, teamB_name = match.get('teamA_name', 'TBD'), match.get('teamB_name', 'TBD')
                flag_a, flag_b = get_country_flag(teamA_name), get_country_flag(teamB_name)
                
                col1, col2, col3 = st.columns([3, 1, 3])
                with col1: st.write(f"**{flag_a} {teamA_name}**")
                with col2: st.write(f"**{match.get('scoreA',0)}-{match.get('scoreB',0)}**" if match.get('status') == 'completed' else "**VS**")
                with col3: st.write(f"**{flag_b} {teamB_name}**")
                
                if match.get('status') == 'completed':
                    st.success(f"✅ Completed - {match.get('method','simulated').title()}")
                    if match.get('goal_scorers'):
                        with st.expander("Goal Scorers"):
                            for goal in match['goal_scorers']:
                                st.write(f"⚽ {goal['player']} ({goal['minute']}') - {goal['team']}")
                    # Show AI commentary for played matches
                    if match.get('method') == 'played' and match.get('commentary'):
                        with st.expander("🎙️ Match Commentary"):
                            for comment in match['commentary']:
                                st.write(f"• {comment}")
                else:
                    st.info("🕐 Scheduled")
                st.divider()

def show_standings_section(teams):
    st.subheader("Team Standings")
    if not teams:
        st.info("No teams registered yet")
        return
    
    sorted_teams = sorted(teams, key=lambda x: x.get('points', 0), reverse=True)
    for i, team in enumerate(sorted_teams):
        flag = get_country_flag(team['country'])
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        with col1: st.write("🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}")
        with col2: st.write(f"**{flag} {team['country']}**")
        with col3: st.write(f"**{team.get('points',0)}** pts")
        with col4: st.write(f"Rating: {team.get('rating',75)}")

def show_top_scorers_section(matches):
    st.subheader("Top Scorers")
    all_goal_scorers = [goal for match in matches if match.get('status') == 'completed' and match.get('goal_scorers') for goal in match['goal_scorers']]
    
    if not all_goal_scorers:
        st.info("No goals scored yet in the tournament")
        return
    
    goal_counts = {}
    for goal in all_goal_scorers:
        goal_counts[goal['player']] = goal_counts.get(goal['player'], 0) + 1
    
    for i, (player, goals) in enumerate(sorted(goal_counts.items(), key=lambda x: x[1], reverse=True)[:10]):
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1: st.write("👑" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}")
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
            st.success("Tournament started!")
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
        # Safely handle team IDs
        teamA_id = safe_objectid_conversion(match.get('teamA_id'))
        teamB_id = safe_objectid_conversion(match.get('teamB_id'))
        
        teamA = db.federations.find_one({"_id": teamA_id})
        teamB = db.federations.find_one({"_id": teamB_id})
        
        if teamA and teamB:
            flag_a, flag_b = get_country_flag(teamA['country']), get_country_flag(teamB['country'])
            match_options.append({
                "match": match, 
                "display": f"{flag_a} {teamA['country']} vs {flag_b} {teamB['country']}",
                "teamA_name": teamA['country'], 
                "teamB_name": teamB['country']
            })
        else:
            # If teams not found, use the stored names
            teamA_name = match.get('teamA_name', 'Unknown Team')
            teamB_name = match.get('teamB_name', 'Unknown Team')
            flag_a, flag_b = get_country_flag(teamA_name), get_country_flag(teamB_name)
            match_options.append({
                "match": match, 
                "display": f"{flag_a} {teamA_name} vs {flag_b} {teamB_name}",
                "teamA_name": teamA_name, 
                "teamB_name": teamB_name
            })
    
    if match_options:
        selected_match_display = st.selectbox("Choose a match:", [m["display"] for m in match_options])
        selected_match_info = next((m for m in match_options if m["display"] == selected_match_display), None)
        
        if selected_match_info:
            teamA_name, teamB_name = selected_match_info['teamA_name'], selected_match_info['teamB_name']
            flag_a, flag_b = get_country_flag(teamA_name), get_country_flag(teamB_name)
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1: st.markdown(f"### {flag_a} {teamA_name}")
            with col2: st.markdown("### VS")
            with col3: st.markdown(f"### {flag_b} {teamB_name}")
