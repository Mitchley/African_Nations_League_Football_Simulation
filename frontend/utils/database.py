from pymongo import MongoClient
from datetime import datetime

def get_database():
    connection_string = "mongodb+srv://mitchleytapiwa2_db_user:D6Zr2jDQhUUmQh0L@cluster0.yp01ize.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(connection_string)
    return client['AfricanLeague']

def save_team(team_data):
    """Save a new team to the database"""
    db = get_database()
    try:
        # Insert federation
        federation_data = {
            "country": team_data["country"],
            "manager": team_data["manager"],
            "email": team_data["representative_email"],
            "representative_name": team_data["representative_name"],
            "rating": team_data["rating"],
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "goalsFor": 0,
            "goalsAgainst": 0,
            "createdAt": datetime.utcnow()
        }
        
        federation_result = db.federations.insert_one(federation_data)
        federation_id = federation_result.inserted_id
        
        # Insert players
        players_data = []
        for player in team_data["players"]:
            player_data = {
                "name": player["name"],
                "naturalPosition": player["natural_position"],
                "ratings": player["ratings"],
                "isCaptain": player["is_captain"],
                "federationId": federation_id,
                "goals": 0,
                "assists": 0,
                "yellowCards": 0,
                "redCards": 0,
                "matchesPlayed": 0,
                "minutesPlayed": 0,
                "createdAt": datetime.utcnow()
            }
            players_data.append(player_data)
        
        if players_data:
            db.players.insert_many(players_data)
        
        return federation_id
    except Exception as e:
        print(f"Error saving team: {e}")
        raise e

def get_all_teams():
    """Get all teams from the database"""
    db = get_database()
    return list(db.federations.find({}))

def get_team_by_email(email):
    """Get team by representative email"""
    db = get_database()
    return db.federations.find_one({"email": email})

def get_players_by_federation(federation_id):
    """Get all players for a federation"""
    db = get_database()
    return list(db.players.find({"federationId": federation_id}))

def update_team_stats(federation_id, stats_update):
    """Update team statistics"""
    db = get_database()
    return db.federations.update_one(
        {"_id": federation_id},
        {"$inc": stats_update}
    )

def get_tournament_matches():
    """Get all tournament matches"""
    db = get_database()
    return list(db.matches.find().sort([("round", 1), ("matchNumber", 1)]))
