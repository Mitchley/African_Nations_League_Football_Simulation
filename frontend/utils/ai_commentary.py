import random
import requests
import os
from frontend.utils.database import get_database

class AICommentaryGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
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
            prompt = f"""
            Generate exciting football match commentary for an African Nations League match between {teamA} and {teamB}.
            
            Match Events: {match_events}
            
            Create realistic, passionate commentary with African football flair. Include:
            - Exciting play-by-play descriptions
            - Cultural references to African football
            - Emotional reactions to goals and key moments
            - Commentary about player performances
            - Atmosphere descriptions
            
            Return 8-12 commentary lines in bullet points.
            """
            
            # This is a placeholder - you'd integrate with actual OpenAI API
            response = f"AI Commentary for {teamA} vs {teamB}: Exciting African football action!"
            
            # Split into individual commentary lines
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
