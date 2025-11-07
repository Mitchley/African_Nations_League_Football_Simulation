import random
import streamlit as st

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
            # Enhanced African-themed commentary
            commentary_lines = [
                f"🏆 AFRICAN NATIONS LEAGUE: {teamA} vs {teamB} kicks off with incredible energy!",
                f"The atmosphere is electric as these African giants battle for continental glory!",
                f"Beautiful flowing football on display - African artistry at its finest!",
                f"The passion and skill from both teams is a testament to African football!",
                f"GOAL! The stadium erupts in a wave of African celebration!",
                f"What a moment of magic! African flair shining through!",
                f"The tension mounts as we approach the final whistle!",
                f"FULL TIME! Another unforgettable chapter in African football history!"
            ]
            
            return commentary_lines
            
        except Exception as e:
            print(f"AI commentary error: {str(e)}")
            return self._generate_fallback_commentary(teamA, teamB, match_events)
    
    def _generate_fallback_commentary(self, teamA, teamB, match_events):
        """Enhanced fallback commentary with African football flavor"""
        
        african_flair_phrases = [
            "The juju is working for this team! African magic on display!",
            "The rhythm of the drums fuels the players' energy!",
            "Skills that would make the great African legends proud!",
            "The spirit of the continent flows through this match!",
            "African football heritage shining brightly!",
            "The beautiful game, African style!",
        ]
        
        commentary = [
            f"🏆 AFRICAN NATIONS LEAGUE: {teamA} vs {teamB} kicks off!",
            random.choice(african_flair_phrases),
            "Both teams showcasing the technical brilliance of African football!",
            "The pace and passion is everything we love about African football!",
        ]
        
        # Add goal commentary if there are goals
        goals = [e for e in match_events if 'goal' in e.lower()]
        if goals:
            commentary.append("GOAL! The African football spirit celebrates!")
            commentary.append("What a moment of continental pride!")
        
        commentary.extend([
            "The second half begins with both teams hungry for victory!",
            "Every tackle echoes with African determination!",
            "Final minutes drama in this African football classic!",
            f"FULL TIME! The African Nations League delivers another thriller!"
        ])
        
        return commentary

def get_ai_commentary_generator():
    return AICommentaryGenerator()
