import streamlit as st
import time
import random
from frontend.utils.auth import init_session_state, login_user, logout_user
from frontend.utils.database import save_team, get_database, get_players_by_federation
from frontend.utils.match_simulator import simulate_match
init_session_state()

AFRICAN_COUNTRIES = ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", "DR Congo", "Egypt", "Ethiopia", "Ghana", "Ivory Coast", "Kenya", "Morocco", "Mozambique", "Nigeria", "Senegal", "South Africa", "Tanzania", "Tunisia", "Uganda", "Zambia", "Zimbabwe"]

class Player:
    def __init__(self, name, position, is_captain=False):
        self.name = name
        self.position = position
        self.is_captain = is_captain

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
    st.subheader("Federation Registration")
    st.info("Register your national team to participate in the tournament")
    
    db = get_database()
    existing_teams = list(db.federations.find({}, {"country": 1}))
    existing_countries = [team['country'] for team in existing_teams]
    available_countries = [c for c in AFRICAN_COUNTRIES if c not in existing_countries]
    
    if not available_countries:
        st.error("🚫 All countries have been registered for this tournament")
        return
    
    country = st.selectbox("**Select Country**", available_countries)
    manager = st.text_input("**Manager Name**")
    representative_name = st.text_input("**Representative Name**")
    representative_email = st.text_input("**Representative Email**")
    password = st.text_input("**Create Password**", type="password")
    
    st.markdown("---")
    st.subheader("👥 Build Your Squad (23 Players)")
    
    # Initialize squad in session state
    if 'squad' not in st.session_state:
        st.session_state.squad = []
    
    # Show current squad status
    squad = st.session_state.squad
    st.write(f"**Squad: {len(squad)}/23 players**")
    
    # ALWAYS show the add player form, but disable when full
    with st.form("add_player_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            player_name = st.text_input("Player Name", placeholder="Enter player name", 
                                      disabled=len(squad) >= 23)
        with col2:
            position = st.selectbox("Position", ["GK", "DF", "MD", "AT"], 
                                  disabled=len(squad) >= 23)
        
        if st.form_submit_button("➕ Add Player", disabled=len(squad) >= 23):
            if player_name:
                # Check for duplicates
                if any(p.name == player_name for p in squad):
                    st.error("❌ Player name already exists in squad")
                else:
                    st.session_state.squad.append(Player(player_name, position))
                    st.success(f"✅ Added {player_name} ({position})")
                    st.rerun()
            else:
                st.error("❌ Please enter a player name")
    
    if len(squad) >= 23:
        st.success("✅ Squad complete! 23/23 players")
    
    # Display squad and captain selection
    if squad:
        st.markdown("---")
        
        # Captain selection
        captain_options = [f"{p.name} ({p.position})" for p in squad]
        selected_captain = st.selectbox("**Select Captain**", captain_options)
        captain_index = captain_options.index(selected_captain)
        
        # Update captain status
        for i, player in enumerate(squad):
            player.is_captain = (i == captain_index)
        
        # Display squad with positions count
        st.write("**Your Squad:**")
        
        # Count positions
        positions = {'GK': 0, 'DF': 0, 'MD': 0, 'AT': 0}
        for player in squad:
            positions[player.position] += 1
        
        st.write(f"**Position breakdown:** GK: {positions['GK']}, DF: {positions['DF']}, MD: {positions['MD']}, AT: {positions['AT']}")
        
        for player in squad:
            captain = " ⭐ CAPTAIN" if player.is_captain else ""
            st.write(f"- {player.name} ({player.position}){captain}")
        
        # Clear squad button
        if st.button("🗑️ Clear Squad"):
            st.session_state.squad = []
            st.rerun()
    
    # Registration button
    st.markdown("---")
    if st.button("🚀 Register Federation", type="primary", use_container_width=True):
        if validate_registration(country, manager, representative_name, representative_email, password, squad):
            success = register_federation(country, manager, representative_name, representative_email, password, squad)
            if success:
                # Auto-login after successful registration
                if login_user(representative_email, password):
                    st.success("🎉 Registration successful! Logging you in...")
                    st.rerun()

def validate_registration(country, manager, rep_name, rep_email, password, squad):
    if not all([country, manager, rep_name, rep_email, password]):
        st.error("❌ Please fill all fields")
        return False
    
    if len(squad) != 23:
        st.error(f"❌ Need exactly 23 players (currently {len(squad)})")
        return False
    
    positions = {'GK': 0, 'DF': 0, 'MD': 0, 'AT': 0}
    for player in squad: positions[player.position] += 1
    
    if positions['GK'] < 2 or positions['DF'] < 6 or positions['MD'] < 6 or positions['AT'] < 3:
        st.error("❌ Invalid squad composition. Need: 2+ GK, 6+ DF, 6+ MD, 3+ AT")
        return False
    
    return True

def register_federation(country, manager, rep_name, rep_email, password, squad):
    try:
        db = get_database()
        
        if db.federations.find_one({"email": rep_email}):
            st.error("❌ Email already registered")
            return False
        
        db.users.insert_one({
            "email": rep_email, "password": password, "role": "federation", 
            "country": country, "createdAt": None
        })
        
        team_data = {
            "country": country, "manager": manager, "representative_name": rep_name,
            "representative_email": rep_email, "rating": 75.0,
            "players": [{
                "name": p.name, "naturalPosition": p.position,
                "ratings": {"GK": 70, "DF": 75, "MD": 78, "AT": 82},
                "isCaptain": p.is_captain
            } for p in squad]
        }
        
        save_team(team_data)
        st.session_state.squad = []
        return True
        
    except Exception as e:
        st.error(f"❌ Registration error: {e}")
        return False

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
            with col1: st.metric("Points", user_team.get('points', 0))
            with col2: st.metric("Rank", f"#{user_team.get('rank', 'N/A')}")

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
        if st.button("🔄 Reset", key="admin_reset"):
            db.matches.update_many({}, {"$set": {"scoreA": 0, "scoreB": 0}})
            st.success("Reset!")
    
    st.markdown("---")
    show_live_sim(db)

def show_live_sim(db):
    st.subheader("⚽ Live Match Simulation")
    
    matches = list(db.matches.find({"status": "scheduled"}).limit(5))
    
    if not matches:
        st.info("No scheduled matches available")
        return
    
    match_options = []
    for match in matches:
        teamA = db.federations.find_one({"_id": match['teamA']})
        teamB = db.federations.find_one({"_id": match['teamB']})
        if teamA and teamB:
            match_options.append({
                "match": match, "display": f"{teamA['country']} vs {teamB['country']}",
                "teamA_name": teamA['country'], "teamB_name": teamB['country']
            })
    
    selected_match_display = st.selectbox("Choose a match to simulate:", [m["display"] for m in match_options], key="match_selector")
    selected_match_info = next((m for m in match_options if m["display"] == selected_match_display), None)
    
    if selected_match_info:
        show_live_match_interface(db, selected_match_info)

def show_live_match_interface(db, match_info):
    if 'match_live' not in st.session_state: st.session_state.match_live = False
    if 'match_minute' not in st.session_state: st.session_state.match_minute = 0
    if 'commentary' not in st.session_state: st.session_state.commentary = []
    if 'score_a' not in st.session_state: st.session_state.score_a = 0
    if 'score_b' not in st.session_state: st.session_state.score_b = 0
    if 'current_match_id' not in st.session_state: st.session_state.current_match_id = None
    
    if st.session_state.current_match_id != match_info['match']['_id']:
        reset_match_state()
        st.session_state.current_match_id = match_info['match']['_id']
    
    teamA_name, teamB_name = match_info['teamA_name'], match_info['teamB_name']
    
    st.markdown("### **African Cup of Nations League**")
    st.markdown(f"**LIVE: {st.session_state.match_minute}'**" if st.session_state.match_live else "**MATCH READY**")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1: st.markdown(f"### {st.session_state.score_a}"); st.markdown(f"**{teamA_name}**")
    with col2: st.markdown("### -")
    with col3: st.markdown(f"### {st.session_state.score_b}"); st.markdown(f"**{teamB_name}**")
    
    if st.session_state.commentary:
        latest_comment = st.session_state.commentary[-1]
        st.info(f"**{latest_comment}**")
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if not st.session_state.match_live:
            if st.button("▶️ Play", key="play_button"): start_match_simulation(teamA_name, teamB_name)
        else:
            if st.button("⏸️ Pause", key="pause_button"): st.session_state.match_live = False
    with col2:
        if st.session_state.match_live:
            if st.button("⏩ Fast forward", key="fast_forward_button"): fast_forward_match(teamA_name, teamB_name)
    with col3:
        if st.button("⚡ Quick sim", key="quick_sim_button"): quick_simulate_match(db, match_info['match'], teamA_name, teamB_name)
    with col4:
        if st.button("🔄 Reset", key="reset_match_button"): reset_match_state()
    
    if st.session_state.commentary:
        st.subheader("📝 Match Events")
        for event in reversed(st.session_state.commentary[-8:]): st.write(f"• {event}")

def start_match_simulation(teamA_name, teamB_name):
    st.session_state.match_live = True
    st.session_state.match_minute = 1
    st.session_state.commentary = [f"Match between {teamA_name} and {teamB_name} kicked off!"]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for minute in range(1, 91):
        if not st.session_state.match_live: break
        st.session_state.match_minute = minute
        progress_bar.progress(minute / 90)
        status_text.text(f"Playing... {minute}'")
        
        event_chance = 0.08 + (minute / 500)
        if random.random() < event_chance:
            event = generate_match_event()
            st.session_state.commentary.append(f"{minute}' - {event}")
            if "GOAL" in event:
                if random.random() < 0.5: st.session_state.score_a += 1
                else: st.session_state.score_b += 1
        
        time.sleep(0.3)
    
    if st.session_state.match_live:
        st.session_state.commentary.append("🏁 Full time! Match ended.")
        st.session_state.match_live = False

def fast_forward_match(teamA_name, teamB_name):
    remaining_time = 90 - st.session_state.match_minute
    status_text = st.empty()
    
    for minute in range(remaining_time):
        st.session_state.match_minute += 1
        status_text.text(f"Fast forwarding... {st.session_state.match_minute}'")
        
        if random.random() < 0.4:
            event = generate_match_event()
            st.session_state.commentary.append(f"{st.session_state.match_minute}' - {event}")
            if "GOAL" in event:
                if random.random() < 0.5: st.session_state.score_a += 1
                else: st.session_state.score_b += 1
        
        time.sleep(0.1)
    
    st.session_state.commentary.append("🏁 Full time! Match ended.")
    st.session_state.match_live = False

def quick_simulate_match(db, match, teamA_name, teamB_name):
    result = simulate_match(match['_id'], 'simulated')
    if result:
        st.session_state.score_a, st.session_state.score_b = result['scoreA'], result['scoreB']
        st.session_state.match_live, st.session_state.match_minute = False, 90
        
        if st.session_state.score_a == 0 and st.session_state.score_b == 0:
            st.session_state.commentary = [
                f"Match between {teamA_name} and {teamB_name} started!",
                "25' - Close chance! Shot goes just wide", "45' - Half time: 0-0",
                "67' - Great save by the goalkeeper!", "89' - Final opportunity goes begging",
                "🏁 Full time! It ends 0-0"
            ]
        else:
            st.session_state.commentary = [
                f"Match between {teamA_name} and {teamB_name} started!",
                f"32' - GOAL! {teamA_name if st.session_state.score_a > 0 else teamB_name} scores!",
                "45' - Half time", "65' - Yellow card shown", "78' - Substitution made",
                "🏁 Full time! Match ended."
            ]
        st.success("✅ Match simulated successfully!")

def reset_match_state():
    st.session_state.match_live = False
    st.session_state.match_minute = 0
    st.session_state.score_a = 0
    st.session_state.score_b = 0
    st.session_state.commentary = []
    st.session_state.current_match_id = None

def generate_match_event():
    events = [
        "Great save by the goalkeeper!", "Corner kick awarded", "Yellow card shown",
        "Free kick in dangerous position", "Shot goes wide of the post", "GOAL! What a fantastic strike!",
        "Substitution made", "Offside called by the assistant referee", "Penalty appeal waved away",
        "Header goes over the bar", "Counter attack!", "Beautiful passing move",
        "Tactical foul stops the attack", "GOAL! Clinical finish!", "Injury break", "VAR check completed"
    ]
    return random.choice(events)

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
        with col2: st.metric("Points", user_team.get('points', 0))
        with col3: st.metric("Rating", user_team.get('rating', 75))
        
        st.subheader("👥 My Squad")
        for player in user_team.get('players', [])[:5]:
            captain = " ⭐" if player.get('isCaptain') else ""
            st.write(f"• {player['name']} ({player.get('naturalPosition', 'Player')}){captain}")
    else:
        st.error("No team found for your account")

def show_tournament():
    """Tournament page with simple bracket design"""
    st.title("🏆 Tournament Bracket")
    db = get_database()
    
    # Get teams from database
    teams = list(db.federations.find({}))
    
    st.header("AFRICAN NATIONS LEAGUE 2025")
    st.subheader("ROAD TO THE FINAL")
    
    # Create two columns for the bracket
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Left Bracket**")
        # Left bracket teams (first 4 teams from database)
        left_teams = teams[:4] if len(teams) >= 4 else teams
        for team in left_teams:
            st.write(f"• **{team['country']}**")
        
        # Add placeholder teams if less than 4
        for _ in range(4 - len(left_teams)):
            st.write("• **TBD**")
    
    with col2:
        st.write("**Right Bracket**")
        # Right bracket teams (next 4 teams from database)
        right_teams = teams[4:8] if len(teams) >= 8 else teams[4:] if len(teams) > 4 else []
        for team in right_teams:
            st.write(f"• **{team['country']}**")
        
        # Add placeholder teams if less than 4
        for _ in range(4 - len(right_teams)):
            st.write("• **TBD**")
    
    # Final match
    st.markdown("---")
    st.write("### 🏆 Final")
    st.write("**Left Bracket Winner vs Right Bracket Winner**")

def show_matches():
    st.title("⚽ Matches & Fixtures")
    db = get_database()
    
    matches = list(db.matches.find({}))
    
    for match in matches:
        teamA = db.federations.find_one({"_id": match['teamA']})
        teamB = db.federations.find_one({"_id": match['teamB']})
        
        if teamA and teamB:
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1: st.write(f"**{teamA['country']} vs {teamB['country']}**")
            with col2: 
                if match.get('status') == 'completed':
                    st.success(f"**{match.get('scoreA', 0)}-{match.get('scoreB', 0)}**")
                else: st.info("VS")
            with col3: st.write(match.get('status', 'scheduled').title())
            st.divider()

def show_statistics():
    st.title("📊 Statistics")
    db = get_database()
    
    st.subheader("🏆 Team Standings")
    teams = list(db.federations.find({}).sort("points", -1))
    
    for team in teams[:5]:
        st.write(f"**{team['country']}** - {team.get('points', 0)} pts")
    
    st.subheader("🥅 Top Scorers")
    st.write("S. Mane (Senegal) - 5 goals")
    st.write("M. Salah (Egypt) - 4 goals")

if __name__ == "__main__":
    main()
