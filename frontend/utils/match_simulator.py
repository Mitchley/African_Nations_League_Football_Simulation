import random
from datetime import datetime
from .database import get_database
from .ai_commentary import generate_match_commentary, display_live_commentary
import streamlit as st

def simulate_match(match_id, simulation_type='simulated'):
    """Simulate match with or without commentary"""
    db = get_database()
    match = db.matches.find_one({"_id": match_id})
    
    if not match or not match.get('teamA') or not match.get('teamB'):
        return None
    
    teamA = db.federations.find_one({"_id": match['teamA']})
    teamB = db.federations.find_one({"_id": match['teamB']})
    
    # Simple simulation logic
    ratingA = teamA.get('rating', 70)
    ratingB = teamB.get('rating', 70)
    
    goalsA = max(0, int((ratingA / 100) * random.uniform(0, 4)))
    goalsB = max(0, int((ratingB / 100) * random.uniform(0, 4)))
    
    if goalsA == goalsB:
        goalsA += random.randint(0, 1)
        goalsB += random.randint(0, 1)
    
    # Update match
    db.matches.update_one(
        {"_id": match_id},
        {"$set": {
            "scoreA": goalsA,
            "scoreB": goalsB,
            "winner": match['teamA'] if goalsA > goalsB else match['teamB'],
            "status": "completed",
            "simulationType": simulation_type,
            "completedAt": datetime.utcnow()
        }}
    )
    
    # Update team stats
    update_team_stats(match['teamA'], match['teamB'], goalsA, goalsB)
    
    return {"scoreA": goalsA, "scoreB": goalsB}

def update_team_stats(teamA_id, teamB_id, goalsA, goalsB):
    """Update team statistics after match"""
    db = get_database()
    
    # Update team A
    db.federations.update_one(
        {"_id": teamA_id},
        {"$inc": {
            "goalsFor": goalsA,
            "goalsAgainst": goalsB,
            "wins": 1 if goalsA > goalsB else 0,
            "losses": 1 if goalsA < goalsB else 0,
            "draws": 1 if goalsA == goalsB else 0
        }}
    )
    
    # Update team B
    db.federations.update_one(
        {"_id": teamB_id},
        {"$inc": {
            "goalsFor": goalsB,
            "goalsAgainst": goalsA,
            "wins": 1 if goalsB > goalsA else 0,
            "losses": 1 if goalsB < goalsA else 0,
            "draws": 1 if goalsA == goalsB else 0
        }}
    )