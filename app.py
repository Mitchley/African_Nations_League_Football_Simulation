import streamlit as st
import random
from datetime import datetime
from frontend.utils.database import get_database, initialize_database, is_database_available

# Initialize
st.set_page_config(page_title="African Nations League", layout="wide", page_icon="⚽")
initialize_database()

# Country flags
COUNTRY_FLAGS = {
    "Algeria": "🇩🇿", "Angola": "🇦🇴", "Benin": "🇧🇯", "Botswana": "🇧🇼",
    "Burkina Faso": "🇧🇫", "Burundi": "🇧🇮", "Cameroon": "🇨🇲", "Cape Verde": "🇨🇻",
    "DR Congo": "🇨🇩", "Egypt": "🇪🇬", "Ethiopia": "🇪🇹", "Ghana": "🇬🇭",
    "Ivory Coast": "🇨🇮", "Kenya": "🇰🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿",
    "Nigeria": "🇳🇬", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "Tanzania": "🇹🇿",
    "Tunisia": "🇹🇳", "Uganda": "🇺🇬", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼"
}

# Professional CSS
st.markdown("""
<style>
.tournament-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    border: 4px solid #FFD700;
}
.stage-column {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem;
    border: 2px solid #dee2e6;
}
.match-card {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #1E3C72;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.winner-card {
    background: linear-gradient(135deg, #FFD700 0%, #FFEC8B 100%);
    border: 3px solid #1E3C72;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="tournament-header">
        <h1 style="margin:0; color: #FFD700; font-size: 2.5em;">🏆 AFRICAN NATIONS LEAGUE 2025</h1>
        <p style="margin:0; font-size: 1.3em; font-weight: bold;">ROAD TO THE FINAL</p>
    </div>
    """, unsafe_allow_html=True)

    db = get_database()
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Start Tournament", use_container_width=True):
            initialize_tournament(db)
    with col2:
        if st.button("⚡ Simulate All", use_container_width=True):
            simulate_all_matches(db)
    with col3:
        if st.button("🔄 Reset", use_container_width=True):
            reset_tournament(db)

    # Tournament bracket
    show_tournament_bracket(db)

def initialize_tournament(db):
    """Create quarter-final matches"""
    teams = list(db.federations.find({}).limit(8))
    if len(teams) < 8:
        st.error(f"Need 8 teams. Currently: {len(teams)}")
        return
    
    random.shuffle(teams)
    db.matches.delete_many({})
    
    # Create quarter-finals
    for i in range(0, 8, 2):
        match_data = {
            "teamA_name": teams[i]["country"],
            "teamB_name": teams[i+1]["country"],
            "stage": "quarterfinal",
            "status": "scheduled",
            "scoreA": 0, "scoreB": 0,
            "created_at": datetime.now()
        }
        db.matches.insert_one(match_data)
    
    db.tournaments.update_one({}, {"$set": {"status": "active", "current_stage": "quarterfinal"}}, upsert=True)
    st.success("🎊 Tournament started! 4 quarter-final matches created.")

def show_tournament_bracket(db):
    """Display the full tournament bracket"""
    matches = list(db.matches.find({}))
    
    if not matches:
        st.info("🎯 Tournament not started. Register 8 teams and click 'Start Tournament'")
        return

    # Create 3-column layout for QF -> SF -> Final
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        show_stage_matches(matches, "quarterfinal", "QUARTER FINALS")
    
    with col2:
        show_stage_matches(matches, "semifinal", "SEMI FINALS")
    
    with col3:
        show_stage_matches(matches, "final", "GRAND FINAL")
        show_champion(matches)

def show_stage_matches(matches, stage, title):
    """Display matches for a specific stage"""
    stage_matches = [m for m in matches if m.get('stage') == stage]
    
    st.markdown(f"<div class='stage-column'><h3>{title}</h3></div>", unsafe_allow_html=True)
    
    if not stage_matches:
        st.info(f"Waiting for previous round...")
        return
    
    for match in stage_matches:
        display_match(match)

def display_match(match):
    """Display a single match card"""
    flag_a = COUNTRY_FLAGS.get(match['teamA_name'], "🏴")
    flag_b = COUNTRY_FLAGS.get(match['teamB_name'], "🏴")
    
    if match.get('status') == 'completed':
        # Show result
        winner_bg = "background: #d4edda;" if match['scoreA'] > match['scoreB'] else "background: #f8f9fa;"
        st.markdown(f"""
        <div class="match-card" style="{winner_bg}">
            <div style="display: flex; justify-content: space-between; align-items: center; font-weight: bold;">
                <span>{flag_a} {match['teamA_name']}</span>
                <span>{match['scoreA']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                <span>{flag_b} {match['teamB_name']}</span>
                <span>{match['scoreB']}</span>
            </div>
            <div style="text-align: center; margin-top: 8px; font-size: 0.8em; color: #666;">
                ✅ Completed
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show who advances (except for final)
        if match.get('stage') != 'final':
            winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
            st.caption(f"➡️ Advances: **{winner}**")
            
    else:
        # Show scheduled match
        st.markdown(f"""
        <div class="match-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold;">{flag_a} {match['teamA_name']}</span>
                <span>VS</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                <span style="font-weight: bold;">{flag_b} {match['teamB_name']}</span>
                <span>⏰</span>
            </div>
            <div style="text-align: center; margin-top: 8px; font-size: 0.8em; color: #666;">
                Scheduled
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        if st.button(f"Play {match['teamA_name']} vs {match['teamB_name']}", key=str(match['_id'])):
            play_match(match)

def show_champion(matches):
    """Display the tournament champion"""
    final_matches = [m for m in matches if m.get('stage') == 'final' and m.get('status') == 'completed']
    
    if final_matches:
        final = final_matches[0]
        winner = final['teamA_name'] if final['scoreA'] > final['scoreB'] else final['teamB_name']
        flag = COUNTRY_FLAGS.get(winner, "🏆")
        
        st.markdown(f"""
        <div class="match-card winner-card">
            <div style="text-align: center; padding: 1rem;">
                <h2 style="color: #1E3C72; margin: 0;">🏆 TOURNAMENT CHAMPION 🏆</h2>
                <h1 style="color: #1E3C72; margin: 1rem 0; font-size: 2em;">{flag} {winner}</h1>
                <p style="color: #1E3C72; margin: 0;">African Nations League 2025</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def play_match(match):
    """Simulate a match"""
    db = get_database()
    
    # Simple match simulation
    score_a = random.randint(0, 3)
    score_b = random.randint(0, 3)
    
    db.matches.update_one(
        {"_id": match["_id"]},
        {"$set": {
            "status": "completed",
            "scoreA": score_a,
            "scoreB": score_b,
            "method": "simulated"
        }}
    )
    
    # Advance to next stage if needed
    advance_tournament(db, match)
    
    st.success(f"Match completed: {match['teamA_name']} {score_a}-{score_b} {match['teamB_name']}")
    st.rerun()

def advance_tournament(db, completed_match):
    """Create next round matches"""
    stage = completed_match.get('stage')
    all_stage_matches = list(db.matches.find({"stage": stage}))
    
    # Check if all matches in current stage are complete
    if all(m.get('status') == 'completed' for m in all_stage_matches):
        if stage == "quarterfinal":
            create_semifinals(db)
        elif stage == "semifinal":
            create_final(db)

def create_semifinals(db):
    """Create semi-finals from quarter-final winners"""
    quarters = list(db.matches.find({"stage": "quarterfinal", "status": "completed"}))
    winners = []
    
    for match in quarters:
        winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
        winners.append(winner)
    
    # Create semi-final matches
    for i in range(0, 4, 2):
        match_data = {
            "teamA_name": winners[i],
            "teamB_name": winners[i+1],
            "stage": "semifinal",
            "status": "scheduled",
            "scoreA": 0, "scoreB": 0,
            "created_at": datetime.now()
        }
        db.matches.insert_one(match_data)
    
    db.tournaments.update_one({}, {"$set": {"current_stage": "semifinal"}})
    st.success("🎉 Semi-finals created!")

def create_final(db):
    """Create final from semi-final winners"""
    semis = list(db.matches.find({"stage": "semifinal", "status": "completed"}))
    winners = []
    
    for match in semis:
        winner = match['teamA_name'] if match['scoreA'] > match['scoreB'] else match['teamB_name']
        winners.append(winner)
    
    # Create final match
    match_data = {
        "teamA_name": winners[0],
        "teamB_name": winners[1],
        "stage": "final",
        "status": "scheduled",
        "scoreA": 0, "scoreB": 0,
        "created_at": datetime.now()
    }
    db.matches.insert_one(match_data)
    
    db.tournaments.update_one({}, {"$set": {"current_stage": "final"}})
    st.success("🎉 Final match created!")

def simulate_all_matches(db):
    """Simulate all scheduled matches"""
    scheduled = list(db.matches.find({"status": "scheduled"}))
    for match in scheduled:
        play_match(match)
    st.success("✅ All matches simulated!")

def reset_tournament(db):
    """Reset tournament data"""
    db.matches.delete_many({})
    db.tournaments.delete_many({})
    st.success("🔄 Tournament reset!")

if __name__ == "__main__":
    main()
