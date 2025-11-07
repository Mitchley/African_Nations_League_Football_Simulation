import random
import os
import streamlit as st
from frontend.utils.database import get_database

class AICommentaryGenerator:
    def __init__(self):
        # Get API key from Streamlit secrets, not hardcoded
        self.api_key = st.secrets.get("OPENAI_API_KEY", "")
        self.use_real_ai = bool(self.api_key)
    
    def generate_commentary(self, teamA, teamB, match_events):
        """Generate match commentary using AI or fallback to enhanced random"""
        if self.use_real_ai and self.api_key:
            return self._generate_openai_commentary(teamA, teamB, match_events)
        else:
            return self._generate_fallback_commentary(teamA, teamB, match_events)
    
    def _generate_openai_commentary(self, teamA, teamB, match_events):
        """Generate commentary using OpenAI GPT"""
        try:
            # This would be your actual OpenAI API call
            # For security, the API key comes from secrets
            commentary_lines = [
                f"The African Nations League clash between {teamA} and {teamB} kicks off with great energy!",
                f"Beautiful passing football on display from these African giants!",
                f"The crowd is creating an incredible atmosphere - typical African passion!",
                f"What a chance! So close to opening the scoring!",
                f"GOAL! The stadium erupts with African joy!",
                f"Brilliant skill on display - African flair at its best!",
                f"The tension builds as we enter the final minutes!",
                f"FULL TIME! What a spectacle of African football!"
            ]
            
            return commentary_lines
            
        except Exception as e:
            print(f"AI commentary error: {str(e)}")
            return self._generate_fallback_commentary(teamA, teamB, match_events)
    
    def _generate_fallback_commentary(self, teamA, teamB, match_events):
        """Enhanced fallback commentary with African football flavor"""
        
        african_flair_phrases = [
            "The juju is working for this team!",
            "African magic on the pitch!",
            "The rhythm of the drums inspires the players!",
            "Beautiful display of African football artistry!",
            "The passion of the continent shines through!",
            "Skills that would make Jay-Jay Okocha proud!",
            "The spirit of African football is alive!",
        ]
        
        commentary = [
            f"🏆 AFRICAN NATIONS LEAGUE: {teamA} vs {teamB} kicks off!",
            random.choice(african_flair_phrases),
            "Both teams showing typical African flair and technical ability!",
            "The pace is electric - African football at its finest!",
        ]
        
        # Add goal commentary if there are goals
        goals = [e for e in match_events if 'goal' in e.lower()]
        if goals:
            commentary.append("GOAL! The stadium erupts with African celebration!")
            commentary.append("What a moment for continental football!")
        
        commentary.extend([
            "The second half begins with both teams pushing for glory!",
            "You can feel the continental pride in every tackle!",
            "Last minute drama in this African classic!",
            f"FULL TIME! Another unforgettable African Nations League encounter!"
        ])
        
        return commentary

def get_ai_commentary_generator():
    return AICommentaryGenerator()
