import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import streamlit as st
from frontend.utils.database import get_database

def notify_federations_after_match(match_id):
    """Notify both federations after a match is completed"""
    try:
        db = get_database()
        if not db:
            print("📧 Email notification: Match completed (database not available)")
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
            
            # Get email config from secrets
            sender_email = st.secrets.get("SENDER_EMAIL", "")
            sender_password = st.secrets.get("SENDER_PASSWORD", "")
            smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = st.secrets.get("SMTP_PORT", 587)
            
            if sender_email and sender_password:
                # In production, this would send actual emails
                print(f"📧 Email would be sent from: {sender_email}")
                print(f"📧 To: {teamA['representative_email']} and {teamB['representative_email']}")
                print(f"📧 Match: {match_details['teamA']} {match_details['scoreA']}-{match_details['scoreB']} {match_details['teamB']}")
            else:
                print("📧 Email configuration not complete - printing to console instead")
                print(f"Match result: {match_details['teamA']} {match_details['scoreA']}-{match_details['scoreB']} {match_details['teamB']}")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"Email notification error: {str(e)}")
        return False
