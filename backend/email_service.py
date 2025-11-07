import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os
from frontend.utils.database import get_database

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
    
    def send_match_result(self, team_email, match_details):
        """Send match results to federation representatives"""
        try:
            message = MimeMultipart()
            message['From'] = self.sender_email
            message['To'] = team_email
            message['Subject'] = f"African Nations League - Match Result: {match_details['teamA']} vs {match_details['teamB']}"
            
            body = f"""
            🏆 AFRICAN NATIONS LEAGUE - MATCH RESULT 🏆
            
            Final Score: {match_details['teamA']} {match_details['scoreA']} - {match_details['scoreB']} {match_details['teamB']}
            
            Match Type: {match_details.get('method', 'Simulated').title()}
            
            Goal Scorers:
            """
            
            for goal in match_details.get('goal_scorers', []):
                body += f"• {goal['player']} ({goal['minute']}') - {goal['team']}\n"
            
            body += f"\n\nThank you for participating in the African Nations League!"
            
            message.attach(MimeText(body, 'plain'))
            
            # For demo purposes, we'll print instead of actually sending
            print(f"📧 Email would be sent to: {team_email}")
            print(f"Subject: {message['Subject']}")
            print(f"Body: {body}")
            
            # Uncomment for actual email sending:
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.sender_email, self.sender_password)
            #     server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Email error: {str(e)}")
            return False

def notify_federations_after_match(match_id):
    """Notify both federations after a match is completed"""
    db = get_database()
    email_service = EmailService()
    
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
        
        # Send to both teams
        email_service.send_match_result(teamA['representative_email'], match_details)
        email_service.send_match_result(teamB['representative_email'], match_details)
        
        return True
    
    return False
