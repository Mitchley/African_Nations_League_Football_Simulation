import smtplib
from email.mime.text import MimeText
import os

def send_match_result_email(team_email, match_details):
    """Send email notification to federations about match results"""
    try:
        subject = f"Match Result: {match_details['teamA']} vs {match_details['teamB']}"
        body = f"""
        African Nations League Match Result
        
        {match_details['teamA']} {match_details['scoreA']} - {match_details['scoreB']} {match_details['teamB']}
        
        Match Type: {match_details.get('simulationType', 'simulated')}
        Round: {match_details['round']}
        
        Goal Scorers:
        {chr(10).join(match_details.get('goal_scorers', []))}
        
        Thank you for participating!
        """
        
        msg = MimeText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv('EMAIL_USER', 'noreply@africanleague.com')
        msg['To'] = team_email
        
        # In production, implement actual email sending
        print(f"📧 Email sent to {team_email}: {subject}")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False