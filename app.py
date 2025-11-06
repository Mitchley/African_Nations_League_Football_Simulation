import streamlit as st
import random
from datetime import datetime
from bson import ObjectId
from frontend.utils.auth import init_session_state, login_user, logout_user
from frontend.utils.database import get_database

# Import from correct paths
try:
    from backend.utils.match_simulator import MatchSimulator
    from backend.email_service import EmailService
except ImportError:
    # Fallback - create simple versions if imports fail
    class MatchSimulator:
        def simulate_match_detailed(self, *args):
            return {'scoreA': random.randint(0, 3), 'scoreB': random.randint(0, 3), 'method': 'played'}
        def simulate_match_quick(self, *args):
            return {'scoreA': random.randint(0, 3), 'scoreB': random.randint(0, 3), 'method': 'simulated'}
    
    class EmailService:
        def send_match_result(self, *args):
            return {'status': 'demo'}

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
                'method': match_data.get('method', 'played'),
                'goal_scorers': match_data.get('goal_scorers', [])
            }
            
            # Send to team A
            email_result_a = email_service.send_match_result(team_a['representative_email'], email_data)
            # Send to team B
            email_result_b = email_service.send_match_result(team_b['representative_email'], email_data)
            
            # Show demo email info
            if email_result_a and email_result_a.get('status') == 'demo':
                with st.expander("📧 Email Notification Demo"):
                    st.write(f"**To:** {team_a['representative_email']}")
                    st.write(f"**Subject:** {email_result_a.get('subject')}")
                    st.text(email_result_a.get('body'))
            
            st.success("📧 Match notifications sent to both teams!")
            
    except Exception as e:
        st.error(f"Failed to send notifications: {e}")

def play_match_with_ai(db, match, teamA_name, teamB_name):
    """Play match with AI commentary"""
    st.info("🔄 Playing match with AI commentary...")
    
    # Simulate match with AI commentary
    result = match_simulator.simulate_match_detailed(None, None, teamA_name, teamB_name)
    
    # Update database
    db.matches.update_one({"_id": match["_id"]}, {"$set": {
        "status": "completed", 
        "scoreA": result['scoreA'], 
        "scoreB": result['scoreB'],
        "goal_scorers": result['goal_scorers'], 
        "commentary": result['commentary'], 
        "method": result['method']
    }})
    
    # Send notifications
    send_match_notifications(db, {
        **match,
        'scoreA': result['scoreA'],
        'scoreB': result['scoreB'],
        'goal_scorers': result['goal_scorers'],
        'method': result['method']
    })
    
    # Update tournament progression
    update_tournament_progression(db, match)
    
    st.success(f"✅ Match completed: {teamA_name} {result['scoreA']}-{result['scoreB']} {teamB_name}")
    
    # Show commentary
    with st.expander("🎙️ AI Match Commentary"):
        for comment in result['commentary']:
            st.write(f"• {comment}")

def simulate_match_quick(db, match, teamA_name, teamB_name):
    """Quick simulation"""
    result = match_simulator.simulate_match_quick(None, None, teamA_name, teamB_name)
    
    db.matches.update_one({"_id": match["_id"]}, {"$set": {
        "status": "completed", 
        "scoreA": result['scoreA'], 
        "scoreB": result['scoreB'],
        "goal_scorers": result['goal_scorers'], 
        "commentary": result['commentary'], 
        "method": result['method']
    }})
    
    # Send notifications
    send_match_notifications(db, {
        **match,
        'scoreA': result['scoreA'],
        'scoreB': result['scoreB'],
        'goal_scorers': result['goal_scorers'],
        'method': result['method']
    })
    
    update_tournament_progression(db, match)
    st.success(f"✅ Match simulated: {teamA_name} {result['scoreA']}-{result['scoreB']} {teamB_name}")

def update_tournament_progression(db, completed_match):
    """Update tournament stage after match completion"""
    current_stage = completed_match.get('stage')
    
    if current_stage == "quarterfinal":
        quarterfinals = list(db.matches.find({"stage": "quarterfinal"}))
        if len([m for m in quarterfinals if m.get('status') == 'completed']) == 4:
            winners = []
            for match in quarterfinals:
                winner_id = match['teamA_id'] if match['scoreA'] > match['scoreB'] else match['teamB_id']
                winner_name = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
                winners.append({"id": winner_id, "name": winner_name})
            
            for i in range(0, 4, 2):
                match_data = {
                    "teamA_id": winners[i]["id"], "teamA_name": winners[i]["name"],
                    "teamB_id": winners[i+1]["id"], "teamB_name": winners[i+1]["name"],
                    "stage": "semifinal", "status": "scheduled", "scoreA": 0, "scoreB": 0,
                    "goal_scorers": [], "commentary": [], "method": "not_played", "created_at": datetime.now()
                }
                db.matches.insert_one(match_data)
            db.tournaments.update_one({}, {"$set": {"current_stage": "semifinal"}})
    
    elif current_stage == "semifinal":
        semifinals = list(db.matches.find({"stage": "semifinal"}))
        if len([m for m in semifinals if m.get('status') == 'completed']) == 2:
            winners = []
            for match in semifinals:
                winner_id = match['teamA_id'] if match['scoreA'] > match['scoreB'] else match['teamB_id']
                winner_name = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
                winners.append({"id": winner_id, "name": winner_name})
            
            match_data = {
                "teamA_id": winners[0]["id"], "teamA_name": winners[0]["name"],
                "teamB_id": winners[1]["id"], "teamB_name": winners[1]["name"],
                "stage": "final", "status": "scheduled", "scoreA": 0, "scoreB": 0,
                "goal_scorers": [], "commentary": [], "method": "not_played", "created_at": datetime.now()
            }
            db.matches.insert_one(match_data)
            db.tournaments.update_one({}, {"$set": {"current_stage": "final"}})

# ... [REST OF THE APP CODE REMAINS THE SAME AS BEFORE, just replace the play_match and simulate_match_quick calls]

def show_live_sim(db):
    st.subheader("⚽ Match Simulation")
    matches = list(db.matches.find({"status": "scheduled"}))
    
    if not matches:
        st.info("No scheduled matches available")
        return
    
    match_options = []
    for match in matches:
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
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎮 Play Match with AI", use_container_width=True):
                    play_match_with_ai(db, selected_match_info['match'], teamA_name, teamB_name)
                    st.rerun()
            with col2:
                if st.button("⚡ Simulate Match", use_container_width=True):
                    simulate_match_quick(db, selected_match_info['match'], teamA_name, teamB_name)
                    st.rerun()

# ... [REST OF THE FUNCTIONS REMAIN THE SAME]

def main():
    st.set_page_config(page_title="African Nations League", layout="wide", page_icon="⚽")
    if not st.session_state.user:
        hide_sidebar()
        show_login_page()
    else:
        show_app()

if __name__ == "__main__":
    main()
