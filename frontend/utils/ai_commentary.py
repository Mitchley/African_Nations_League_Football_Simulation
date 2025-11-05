import random
import streamlit as st
from time import sleep

def generate_match_commentary(teamA, teamB, match_events):
    """Generate full match commentary with play-by-play"""
    
    commentary = []
    
    # Pre-match
    commentary.append(f"🏟️ WELCOME to this African Nations League clash between {teamA} and {teamB}!")
    commentary.append("🟢 The match is underway! Both teams looking sharp early on.")
    
    # Generate match events with commentary
    for minute in range(5, 91, random.randint(8, 15)):
        event_type = random.choice(['attack', 'save', 'foul', 'corner', 'shot', 'miss'])
        
        if event_type == 'attack':
            team = random.choice([teamA, teamB])
            commentary.append(f"⚡ {minute}' - Great attacking play from {team}! They're putting pressure on the defense.")
        
        elif event_type == 'save':
            commentary.append(f"🧤 {minute}' - INCREDIBLE SAVE! The goalkeeper denies a certain goal!")
        
        elif event_type == 'foul':
            team = random.choice([teamA, teamB])
            commentary.append(f"🟨 {minute}' - Free kick for {team} in a dangerous position after a foul.")
        
        elif event_type == 'shot':
            team = random.choice([teamA, teamB])
            commentary.append(f"🎯 {minute}' - SHOT! Just wide of the post from {team}!")
    
    # Add some goals randomly
    goals = []
    for _ in range(random.randint(1, 4)):
        minute = random.randint(15, 85)
        scoring_team = random.choice([teamA, teamB])
        goals.append((minute, scoring_team))
    
    goals.sort()  # Sort by minute
    
    for minute, team in goals:
        commentary.append(f"")
        commentary.append(f"⚽⚽⚽ GOOOOOOAL! {minute}' - {team} SCORES! WHAT A FINISH! ⚽⚽⚽")
        commentary.append(f"🎉 The fans are going wild! {team} takes the lead!")
    
    # Half-time and full-time
    commentary.append("")
    commentary.append("🔄 HALF-TIME! What an exciting first 45 minutes!")
    commentary.append("🟢 Second half is underway!")
    commentary.append("")
    commentary.append("🏁 FULL-TIME! The referee blows the final whistle!")
    
    return commentary, goals

def display_live_commentary(commentary):
    """Display commentary in real-time with delays"""
    commentary_container = st.empty()
    
    full_text = ""
    for line in commentary:
        full_text += line + "\n\n"
        commentary_container.markdown(full_text)
        sleep(1.5)  # Delay between commentary lines
    
    return full_text

def generate_commentary(teamA, teamB, action_type, minute):
    """Simple commentary for quick actions"""
    commentaries = {
        'goal': [
            f"⚽ {minute}' GOAL! {teamA} with a spectacular finish!",
            f"⚽ {minute}' WHAT A STRIKE! {teamB} takes the lead!",
        ],
        'save': [
            f"🧤 {minute}' Incredible save by the goalkeeper!",
            f"🧤 {minute}' What a stop! Unbelievable reflexes!",
        ],
        'foul': [
            f"🟨 {minute}' Strong challenge, referee shows a yellow card",
            f"⚔️ {minute}' Physical play in midfield, free kick given",
        ]
    }
    return random.choice(commentaries.get(action_type, [f"⏱️ {minute}' Action in progress..."]))