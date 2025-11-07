import streamlit as st
from frontend.utils.database import get_database

def notify_federations_after_match(match_id):
    """Notify both federations after a match is completed"""
    try:
        db = get_database()
        if not db:
            print("📧 Email notification (demo mode): Match completed")
            return True
        
        match = db.matches.find_one({"_id": match_id})
        if not match:
            return False
        
        # Get federation emails
        teamA = db.federations.find_one({"_id": match['teamA_id']})
        teamB = db.federations.find_one({"_id": match['teamB_id']})
        
        if teamA and teamB:
            match_details = {
                'teamA': match['teamA_name'],
                'teamB': match['teamB_name'],
                'scoreA': match['scoreA'],
                'scoreB': match['scoreB'],
                'goal_scorers': match.get('goal_scorers', []),
                'method': match.get('method', 'simulated')
            }
            
            # In demo mode, just print the notification
            print(f"📧 Email would be sent to: {teamA['representative_email']}")
            print(f"📧 Email would be sent to: {teamB['representative_email']}")
            print(f"Match: {match_details['teamA']} {match_details['scoreA']}-{match_details['scoreB']} {match_details['teamB']}")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"Email notification error: {str(e)}")
        return False
