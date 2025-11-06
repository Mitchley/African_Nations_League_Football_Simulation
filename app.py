import streamlit as st
import random
from datetime import datetime
from bson import ObjectId
import os
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['AfricanLeague']

# Authentication functions
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None

def login_user(email, password):
    user = db.users.find_one({"email": email, "password": password})
    if user:
        st.session_state.user = user
        st.session_state.role = user['role']
        return True
    return False

def logout_user():
    st.session_state.user = None
    st.session_state.role = None

# Services
class EmailService:
    def __init__(self):
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.email = 'tapiwadinner8@gmail.com'
        self.password = 'jyuc frsj uxdf bjle'
    
    def send_match_result(self, recipient_email, match_data):
        try:
            subject = f"🏆 African Nations League - Match Result: {match_data['teamA']} vs {match_data['teamB']}"
            
            body = f"""
🏆 AFRICAN NATIONS LEAGUE - OFFICIAL MATCH RESULT

{match_data['teamA']} {match_data['scoreA']} - {match_data['scoreB']} {match_data['teamB']}

Stage: {match_data['stage'].title()}
Method: {match_data.get('method', 'played').title()}

Goal Scorers:
"""
            if match_data.get('goal_scorers'):
                for goal in match_data['goal_scorers']:
                    body += f"⚽ {goal['player']} ({goal['minute']}') - {goal['team']}\n"
            else:
                body += "No goals scored\n"
            
            body += "\nThank you for participating!\nAfrican Nations League Organization"
            
            msg = MimeMultipart()
            msg['From'] = self.email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            st.error(f"Email error: {e}")
            return False

class AICommentaryGenerator:
    def generate_match_commentary(self, team_a, team_b, events):
        commentary = [f"Welcome to the African Nations League clash between {team_a} and {team_b}!"]
        commentary.append("The atmosphere is electric in the stadium!")
        
        goals = [e for e in events if e['type'] == 'goal']
        for goal in goals:
            commentary.append(f"{goal['minute']}' - GOAL! {goal['player']} scores for {goal['team']}! Amazing finish!")
        
        if goals:
            commentary.append("What an entertaining match with fantastic goals!")
        else:
            commentary.append("A tight tactical battle between two well-matched teams!")
        
        commentary.append("Full time! What a spectacle of African football!")
        return commentary

class MatchSimulator:
    def __init__(self):
        self.commentary_gen = AICommentaryGenerator()
    
    def simulate_match_detailed(self, team_a, team_b, team_a_name, team_b_name):
        events = []
        score_a, score_b = 0, 0
        
        # 90 minutes simulation
        for minute in range(1, 91):
            if random.random() < 0.04:  # Goal
                if random.random() < 0.5:
                    score_a += 1
                    events.append({
                        'type': 'goal', 
                        'team': team_a_name, 
                        'player': f"Player {random.randint(1, 23)}",
                        'minute': minute
                    })
                else:
                    score_b += 1
                    events.append({
                        'type': 'goal', 
                        'team': team_b_name, 
                        'player': f"Player {random.randint(1, 23)}",
                        'minute': minute
                    })
        
        # Extra time if draw
        if score_a == score_b:
            for minute in range(91, 121):
                if random.random() < 0.06:
                    if random.random() < 0.5:
                        score_a += 1
                        events.append({'type': 'goal', 'team': team_a_name, 'player': f"Player {random.randint(1, 23)}", 'minute': minute})
                    else:
                        score_b += 1
                        events.append({'type': 'goal', 'team': team_b_name, 'player': f"Player {random.randint(1, 23)}", 'minute': minute})
            
            # Penalties if still draw
            if score_a == score_b:
                pen_a, pen_b = self.simulate_penalties()
                events.append({'type': 'penalties', 'teamA_penalties': pen_a, 'teamB_penalties': pen_b})
                if pen_a > pen_b:
                    score_a += 1
                else:
                    score_b += 1
        
        commentary = self.commentary_gen.generate_match_commentary(team_a_name, team_b_name, events)
        goal_scorers = [e for e in events if e['type'] == 'goal']
        
        return {
            'scoreA': score_a, 'scoreB': score_b, 'goal_scorers': goal_scorers,
            'commentary': commentary, 'method': 'played'
        }
    
    def simulate_penalties(self):
        a, b = 0, 0
        for _ in range(5):
            if random.random() < 0.7: a += 1
            if random.random() < 0.7: b += 1
        while a == b:
            if random.random() < 0.7: a += 1
            if random.random() < 0.7: b += 1
        return a, b
    
    def simulate_match_quick(self, team_a, team_b, team_a_name, team_b_name):
        score_a, score_b = random.randint(0, 3), random.randint(0, 3)
        goal_scorers = []
        for i in range(score_a):
            goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": random.randint(1, 90), "team": team_a_name})
        for i in range(score_b):
            goal_scorers.append({"player": f"Player {random.randint(1, 23)}", "minute": random.randint(1, 90), "team": team_b_name})
        
        return {
            'scoreA': score_a, 'scoreB': score_b, 'goal_scorers': goal_scorers,
            'commentary': [f"Quick simulation: {team_a_name} {score_a}-{score_b} {team_b_name}"], 'method': 'simulated'
        }

# Initialize services
match_simulator = MatchSimulator()
email_service = EmailService()
init_session_state()

# Constants
AFRICAN_COUNTRIES = ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", "DR Congo", "Egypt", "Ethiopia", "Ghana", "Ivory Coast", "Kenya", "Morocco", "Mozambique", "Nigeria", "Senegal", "South Africa", "Tanzania", "Tunisia", "Uganda", "Zambia", "Zimbabwe"]
COUNTRY_FLAGS = {
    "Algeria": "🇩🇿", "Angola": "🇦🇴", "Benin": "🇧🇯", "Botswana": "🇧🇼",
    "Burkina Faso": "🇧🇫", "Burundi": "🇧🇮", "Cameroon": "🇨🇲", "Cape Verde": "🇨🇻",
    "DR Congo": "🇨🇩", "Egypt": "🇪🇬", "Ethiopia": "🇪🇹", "Ghana": "🇬🇭",
    "Ivory Coast": "🇨🇮", "Kenya": "🇰🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿",
    "Nigeria": "🇳🇬", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "Tanzania": "🇹🇿",
    "Tunisia": "🇹🇳", "Uganda": "🇺🇬", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼"
}

class Player:
    def __init__(self, name, position, is_captain=False):
        self.name = name
        self.position = position
        self.is_captain = is_captain

def generate_player_ratings(position):
    return {pos: random.randint(50, 100) if pos == position else random.randint(0, 50) 
            for pos in ["GK", "DF", "MD", "AT"]}

def get_country_flag(country):
    return COUNTRY_FLAGS.get(country, "🏴")

def safe_objectid_conversion(obj_id):
    if isinstance(obj_id, ObjectId):
        return obj_id
    try:
        return ObjectId(obj_id)
    except:
        return obj_id

def send_match_notifications(match_data):
    try:
        team_a = db.federations.find_one({"_id": safe_objectid_conversion(match_data['teamA'])})
        team_b = db.federations.find_one({"_id": safe_objectid_conversion(match_data['teamB'])})
        
        if team_a and team_b:
            email_data = {
                'teamA': match_data['teamA_name'],
                'teamB': match_data['teamB_name'],
                'scoreA': match_data['scoreA'],
                'scoreB': match_data['scoreB'],
                'stage': match_data['round'],
                'method': match_data.get('simulationType', 'played'),
                'goal_scorers': match_data.get('goals', [])
            }
            
            email_service.send_match_result(team_a['representative_email'], email_data)
            email_service.send_match_result(team_b['representative_email'], email_data)
            st.success("📧 Match notifications sent!")
            
    except Exception as e:
        st.error(f"Notification error: {e}")

def play_match_with_ai(match, teamA_name, teamB_name):
    st.info("🔄 Playing match with AI commentary...")
    
    with st.spinner("Generating AI commentary..."):
        result = match_simulator.simulate_match_detailed(None, None, teamA_name, teamB_name)
    
    db.matches.update_one({"_id": match["_id"]}, {"$set": {
        "status": "completed", 
        "scoreA": result['scoreA'], 
        "scoreB": result['scoreB'],
        "goals": result['goal_scorers'], 
        "commentary": result['commentary'], 
        "simulationType": result['method'],
        "winner": match['teamA'] if result['scoreA'] > result['scoreB'] else match['teamB']
    }})
    
    send_match_notifications({
        **match,
        'scoreA': result['scoreA'],
        'scoreB': result['scoreB'],
        'goals': result['goal_scorers'],
        'simulationType': result['method']
    })
    
    update_tournament_progression(match)
    st.success(f"✅ Match completed: {teamA_name} {result['scoreA']}-{result['scoreB']} {teamB_name}")
    
    with st.expander("🎙️ AI Match Commentary"):
        for comment in result['commentary']:
            st.write(f"• {comment}")

def simulate_match_quick(match, teamA_name, teamB_name):
    result = match_simulator.simulate_match_quick(None, None, teamA_name, teamB_name)
    
    db.matches.update_one({"_id": match["_id"]}, {"$set": {
        "status": "completed", 
        "scoreA": result['scoreA'], 
        "scoreB': result['scoreB'],
        "goals": result['goal_scorers'], 
        "commentary": result['commentary'], 
        "simulationType": result['method'],
        "winner": match['teamA'] if result['scoreA'] > result['scoreB'] else match['teamB']
    }})
    
    send_match_notifications({
        **match,
        'scoreA': result['scoreA'],
        'scoreB': result['scoreB'],
        'goals': result['goal_scorers'],
        'simulationType': result['method']
    })
    
    update_tournament_progression(match)
    st.success(f"✅ Match simulated: {teamA_name} {result['scoreA']}-{result['scoreB']} {teamB_name}")

def update_tournament_progression(completed_match):
    current_round = completed_match.get('round')
    
    if current_round == "quarterfinal":
        quarters = list(db.matches.find({"round": "quarterfinal", "status": "completed"}))
        if len(quarters) == 4:
            # Get winners and create semifinals
            winners = []
            for match in quarters:
                winner_id = match['teamA'] if match['scoreA'] > match['scoreB'] else match['teamB']
                winner_name = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
                winners.append({"id": winner_id, "name": winner_name})
            
            # Update semifinal matches with winners
            semis = list(db.matches.find({"round": "semifinal"}))
            for i, semi in enumerate(semis[:2]):
                if i*2 < len(winners):
                    db.matches.update_one({"_id": semi['_id']}, {"$set": {
                        "teamA": winners[i*2]["id"], "teamA_name": winners[i*2]["name"],
                        "teamB": winners[i*2+1]["id"], "teamB_name": winners[i*2+1]["name"]
                    }})
            
            db.tournaments.update_one({}, {"$set": {"currentRound": "semifinal"}})
    
    elif current_round == "semifinal":
        semis = list(db.matches.find({"round": "semifinal", "status": "completed"}))
        if len(semis) == 2:
            winners = []
            for match in semis:
                winner_id = match['teamA'] if match['scoreA'] > match['scoreB'] else match['teamB']
                winner_name = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
                winners.append({"id": winner_id, "name": winner_name})
            
            # Update final match
            final = db.matches.find_one({"round": "final"})
            if final and len(winners) == 2:
                db.matches.update_one({"_id": final['_id']}, {"$set": {
                    "teamA": winners[0]["id"], "teamA_name": winners[0]["name"],
                    "teamB": winners[1]["id"], "teamB_name": winners[1]["name"]
                }})
            
            db.tournaments.update_one({}, {"$set": {"currentRound": "final"}})

# Main App
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
        password = st.text_input("**Password**", type="password", placeholder="admin123")
        if st.form_submit_button("🚀 **Login as Admin**", use_container_width=True):
            if email and password and login_user(email, password):
                st.success("✅ Admin login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

def show_visitor_access():
    st.subheader("Visitor Access")
    if st.button("👀 **Enter as Visitor**", use_container_width=True, type="primary"):
        st.session_state.user = {"email": "visitor@africanleague.com", "role": "visitor"}
        st.session_state.role = "visitor"
        st.success("🎉 Welcome! Entering as visitor...")
        st.rerun()

def show_federation_registration():
    st.subheader("🇺🇳 Federation Registration")
    existing_teams = db.federations.count_documents({})
    st.info(f"📊 Current teams: {existing_teams}/8")
    
    if 'squad' not in st.session_state:
        st.session_state.squad = []
    
    squad = st.session_state.squad
    
    col1, col2 = st.columns([3, 1])
    with col1:
        player_name = st.text_input("Player Name", placeholder="Enter player name")
    with col2:
        pos_count = {'GK': 0, 'DF': 0, 'MD': 0, 'AT': 0}
        for player in squad:
            pos_count[player.position] += 1
        
        available_positions = [pos for pos in ["GK", "DF", "MD", "AT"] 
                             if pos_count[pos] < (3 if pos == "GK" else 8 if pos == "DF" else 8 if pos == "MD" else 4)]
        position = st.selectbox("Position", available_positions, disabled=not available_positions)
    
    if st.button("➕ Add Player", disabled=(len(squad) >= 23 or not player_name)):
        if player_name and len(squad) < 23:
            st.session_state.squad.append(Player(player_name, position))
            st.rerun()
    
    st.write(f"**Squad: {len(squad)}/23 players**")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Goalkeepers", f"{pos_count['GK']}/3")
    with col2: st.metric("Defenders", f"{pos_count['DF']}/8")
    with col3: st.metric("Midfielders", f"{pos_count['MD']}/8")
    with col4: st.metric("Attackers", f"{pos_count['AT']}/4")
    
    if squad and len(squad) == 23:
        captain_options = [f"{p.name} ({p.position})" for p in squad]
        selected_captain = st.selectbox("Select Captain", captain_options)
        captain_index = captain_options.index(selected_captain)
        for i, player in enumerate(squad):
            player.is_captain = (i == captain_index)
    
    if squad and st.button("🗑️ Clear Squad"):
        st.session_state.squad = []
        st.rerun()
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("Country", [c for c in AFRICAN_COUNTRIES if not db.federations.find_one({"country": c})])
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
        if db.users.find_one({"email": rep_email}):
            st.error("❌ Email already registered")
            return False
        if db.federations.find_one({"country": country}):
            st.error("❌ Country already registered")
            return False
        
        # Create user
        db.users.insert_one({
            "email": rep_email, "password": password, "role": "federation", 
            "country": country, "createdAt": datetime.utcnow()
        })
        
        # Create federation
        federation_data = {
            "country": country, "manager": manager, "representative_name": rep_name,
            "representative_email": rep_email, "rating": random.randint(70, 85),
            "points": 0, "registered_at": datetime.utcnow()
        }
        fed_result = db.federations.insert_one(federation_data)
        
        # Create players
        players = []
        for i, player in enumerate(squad):
            player_data = {
                "name": player.name,
                "country": country,
                "jerseyNumber": i + 1,
                "naturalPosition": player.position,
                "ratings": generate_player_ratings(player.position),
                "federationId": fed_result.inserted_id,
                "isCaptain": player.is_captain,
                "createdAt": datetime.utcnow()
            }
            players.append(player_data)
        
        db.players.insert_many(players)
        
        # Update tournament if 8 teams reached
        team_count = db.federations.count_documents({})
        if team_count >= 8:
            db.tournaments.update_one({}, {"$set": {"status": "active"}})
            st.balloons()
            st.success("🎊 Tournament started with 8 teams!")
        
        st.session_state.squad = []
        return True
        
    except Exception as e:
        st.error(f"❌ Registration error: {str(e)}")
        return False

def show_app():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    with st.sidebar:
        if st.session_state.role == "visitor":
            st.markdown("### 👋 Welcome, Visitor!")
            pages = ["🏠 Home", "🏆 Tournament", "📊 Statistics"]
        else:
            st.markdown(f"### 👋 Welcome, {st.session_state.user['email']}!")
            pages = ["🏠 Home", "👨‍💼 Admin", "🏆 Tournament", "📈 Progress", "📊 Statistics"] if st.session_state.role == "admin" else ["🏠 Home", "🇺🇳 Federation", "🏆 Tournament", "📈 Progress", "📊 Statistics"]
        
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
    pages = {
        "🏠 Home": show_home, "👨‍💼 Admin": show_admin, "🇺🇳 Federation": show_federation,
        "🏆 Tournament": show_tournament, "📈 Progress": show_progress, "📊 Statistics": show_statistics
    }
    pages.get(st.session_state.current_page, show_home)()

def show_home():
    st.title("🏠 African Nations League")
    teams = list(db.federations.find({}))
    matches = list(db.matches.find({}))
    tournament = db.tournaments.find_one({}) or {}
    
    st.markdown(f"### Welcome back, {st.session_state.user['email']}!")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Teams", len(teams))
    with col2: st.metric("Matches Played", len([m for m in matches if m.get('status') == 'completed']))
    with col3: st.metric("Total Matches", len(matches))
    with col4: st.metric("Tournament Status", tournament.get('status', 'pending').title())
    
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["🏆 Teams", "📊 Standings", "🎯 Top Scorers"])
    with tab1: show_teams(teams)
    with tab2: show_standings(teams)
    with tab3: show_top_scorers()

def show_teams(teams):
    for team in teams:
        flag = get_country_flag(team['country'])
        st.write(f"**{flag} {team['country']}** - Manager: {team.get('manager', 'Unknown')} - Rating: {team.get('rating', 75)}")

def show_standings(teams):
    sorted_teams = sorted(teams, key=lambda x: x.get('points', 0), reverse=True)
    for i, team in enumerate(sorted_teams):
        flag = get_country_flag(team['country'])
        st.write(f"**#{i+1} {flag} {team['country']}** - {team.get('points', 0)} pts")

def show_top_scorers():
    matches = list(db.matches.find({"status": "completed"}))
    all_goals = [goal for match in matches if match.get('goals') for goal in match['goals']]
    
    if not all_goals:
        st.info("No goals scored yet")
        return
    
    goal_counts = {}
    for goal in all_goals:
        goal_counts[goal['player']] = goal_counts.get(goal['player'], 0) + 1
    
    for i, (player, goals) in enumerate(sorted(goal_counts.items(), key=lambda x: x[1], reverse=True)[:5]):
        st.write(f"{i+1}. **{player}** - {goals} goal{'s' if goals > 1 else ''}")

def show_admin():
    if st.session_state.role != 'admin':
        st.error("🔒 Admin access only")
        return
    
    st.title("👨‍💼 Admin Panel")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Tournament"):
            db.tournaments.update_one({}, {"$set": {"status": "active"}})
            st.success("Tournament started!")
    with col2:
        if st.button("🔄 Reset Tournament"):
            db.matches.update_many({}, {"$set": {"status": "scheduled", "scoreA": 0, "scoreB": 0, "goals": [], "winner": None}})
            db.tournaments.update_one({}, {"$set": {"currentRound": "quarterfinal", "status": "active"}})
            st.success("Tournament reset!")
    
    st.markdown("---")
    show_match_simulation()

def show_match_simulation():
    st.subheader("⚽ Match Simulation")
    matches = list(db.matches.find({"status": "scheduled", "teamA": {"$ne": None}, "teamB": {"$ne": None}}))
    
    if not matches:
        st.info("No scheduled matches available")
        return
    
    for match in matches:
        teamA_name, teamB_name = match.get('teamA_name', 'TBD'), match.get('teamB_name', 'TBD')
        flag_a, flag_b = get_country_flag(teamA_name), get_country_flag(teamB_name)
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1: st.write(f"**{flag_a} {teamA_name}**")
        with col2: st.write("**VS**")
        with col3: st.write(f"**{flag_b} {teamB_name}**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🎮 Play {teamA_name} vs {teamB_name}", key=f"play_{match['_id']}"):
                play_match_with_ai(match, teamA_name, teamB_name)
                st.rerun()
        with col2:
            if st.button(f"⚡ Simulate {teamA_name} vs {teamB_name}", key=f"sim_{match['_id']}"):
                simulate_match_quick(match, teamA_name, teamB_name)
                st.rerun()
        st.divider()

def show_federation():
    if st.session_state.role != 'federation':
        st.info("👤 Federation access only")
        return
    
    st.title("🇺🇳 My Federation")
    user_team = db.federations.find_one({"representative_email": st.session_state.user['email']})
    
    if user_team:
        flag = get_country_flag(user_team['country'])
        st.write(f"**{flag} {user_team['country']}**")
        st.write(f"**Manager:** {user_team.get('manager', 'Unknown')}")
        st.write(f"**Rating:** {user_team.get('rating', 75)}")
        st.write(f"**Points:** {user_team.get('points', 0)}")

def show_tournament():
    st.title("🏆 Tournament Bracket")
    matches = list(db.matches.find({}).sort("round", 1))
    tournament = db.tournaments.find_one({}) or {}
    
    st.header("AFRICAN NATIONS LEAGUE 2025")
    st.info(f"**Current Stage: {tournament.get('currentRound', 'quarterfinal').upper()}**")
    
    # Display matches by round
    for round_name in ["quarterfinal", "semifinal", "final"]:
        round_matches = [m for m in matches if m.get('round') == round_name]
        if round_matches:
            st.subheader(f"{round_name.upper().replace('FINAL', 'FINALS')}")
            for match in round_matches:
                teamA, teamB = match.get('teamA_name', 'TBD'), match.get('teamB_name', 'TBD')
                flag_a, flag_b = get_country_flag(teamA), get_country_flag(teamB)
                
                col1, col2, col3 = st.columns([3, 1, 3])
                with col1: st.write(f"**{flag_a} {teamA}**")
                with col2: st.write(f"**{match.get('scoreA', 0)}-{match.get('scoreB', 0)}**" if match.get('status') == 'completed' else "**VS**")
                with col3: st.write(f"**{flag_b} {teamB}**")
                
                if match.get('status') == 'completed':
                    st.success("✅ Completed")
                    if match.get('goals'):
                        with st.expander("Goal Scorers"):
                            for goal in match['goals']:
                                st.write(f"⚽ {goal['player']} ({goal['minute']}')")
                    if match.get('simulationType') == 'played' and match.get('commentary'):
                        with st.expander("🎙️ Commentary"):
                            for comment in match['commentary']:
                                st.write(f"• {comment}")
                else:
                    st.info("🕐 Scheduled")
                st.divider()

def show_progress():
    st.title("📈 Tournament Progress")
    matches = list(db.matches.find({}))
    tournament = db.tournaments.find_one({}) or {}
    
    st.info(f"**Current Stage: {tournament.get('currentRound', 'quarterfinal').upper()}**")
    
    completed = len([m for m in matches if m.get('status') == 'completed'])
    total = len(matches)
    
    st.metric("Matches Completed", f"{completed}/{total}")
    
    for match in matches:
        if match.get('status') == 'completed':
            teamA, teamB = match.get('teamA_name', 'TBD'), match.get('teamB_name', 'TBD')
            st.success(f"✅ {teamA} {match.get('scoreA', 0)}-{match.get('scoreB', 0)} {teamB} ({match.get('round')})")

def show_statistics():
    st.title("📊 Statistics")
    show_standings(list(db.federations.find({})))
    st.markdown("---")
    show_top_scorers()

if __name__ == "__main__":
    main()
