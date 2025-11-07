import random
from datetime import datetime
from frontend.utils.ai_commentary import get_ai_commentary_generator
from backend.email_service import notify_federations_after_match

def simulate_match_with_commentary(db, match_id, teamA_name, teamB_name):
    """Enhanced match simulation with AI commentary"""
    ai_generator = get_ai_commentary_generator()
    
    # Get team ratings for more realistic simulation
    match = db.matches.find_one({"_id": match_id}) if db else None
    teamA = db.federations.find_one({"_id": match['teamA_id']}) if db and match else None
    teamB = db.federations.find_one({"_id": match['teamB_id']}) if db and match else None
    
    ratingA = teamA.get('rating', 75) if teamA else 75
    ratingB = teamB.get('rating', 75) if teamB else 75
    
    # Calculate goal probabilities based on ratings
    goal_prob_a = min(0.08 + (ratingA - 75) * 0.002, 0.15)
    goal_prob_b = min(0.08 + (ratingB - 75) * 0.002, 0.15)
    
    commentary = []
    score_a, score_b = 0, 0
    goal_scorers = []
    match_events = []
    
    # First half
    commentary.append(f"🏆 AFRICAN NATIONS LEAGUE: {teamA_name} vs {teamB_name} kicks off!")
    
    for minute in range(1, 46):
        event_occurred = False
        
        # Team A goal chance
        if random.random() < goal_prob_a:
            score_a += 1
            goal_scorers.append({
                "player": f"Player {random.randint(1, 23)}",
                "minute": minute,
                "team": teamA_name
            })
            match_events.append(f"Goal for {teamA_name} at {minute}'")
            event_occurred = True
        
        # Team B goal chance  
        elif random.random() < goal_prob_b:
            score_b += 1
            goal_scorers.append({
                "player": f"Player {random.randint(1, 23)}",
                "minute": minute, 
                "team": teamB_name
            })
            match_events.append(f"Goal for {teamB_name} at {minute}'")
            event_occurred = True
        
        # Other match events
        elif random.random() < 0.05:
            events = ["Great save!", "Close miss!", "Yellow card!", "Tactical substitution"]
            match_events.append(f"{random.choice(events)} at {minute}'")
            event_occurred = True
    
    # Generate AI commentary based on match events
    ai_commentary = ai_generator.generate_commentary(teamA_name, teamB_name, match_events)
    commentary.extend(ai_commentary)
    
    # Update match in database
    if db:
        db.matches.update_one(
            {"_id": match_id},
            {"$set": {
                "status": "completed",
                "scoreA": score_a,
                "scoreB": score_b,
                "goal_scorers": goal_scorers,
                "commentary": commentary,
                "method": "played"
            }}
        )
    
    # Send email notifications
    notify_federations_after_match(match_id)
    
    return score_a, score_b, goal_scorers, commentary
