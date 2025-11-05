import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def initialize_database():
    print("🚀 Initializing African Nations League Database...")
    
    # Connect to MongoDB
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client['AfricanLeague']
    
    # Clear existing data (optional - comment out if you want to keep data)
    print("🗑️ Clearing existing data...")
    for collection in ['users', 'federations', 'players', 'tournaments', 'matches', 'player_stats']:
        db[collection].delete_many({})
    
    # Create admin users
    print("👨‍💼 Creating admin users...")
    db.users.insert_many([
        {
            "email": "admin@africanleague.com", 
            "password": "admin123", 
            "role": "admin", 
            "createdAt": datetime.utcnow()
        },
        {
            "email": "ammarcanani@gmail.com", 
            "password": "admin123", 
            "role": "admin", 
            "createdAt": datetime.utcnow()
        },
        {
            "email": "elsje.scott@uct.ac.za", 
            "password": "admin123", 
            "role": "admin", 
            "createdAt": datetime.utcnow()
        }
    ])
    
    # African countries for the tournament
    countries = [
        "Nigeria", "Egypt", "Senegal", "Ghana", 
        "Morocco", "Cameroon", "Ivory Coast", "Algeria"
    ]
    
    # Create 8 federations (7 pre-registered + 1 slot for demo)
    print("🇺🇳 Creating federations and players...")
    federation_ids = []
    
    for i, country in enumerate(countries[:7]):  # First 7 countries as pre-registered
        # Create federation
        federation = {
            "country": country,
            "manager": f"Manager of {country}",
            "email": f"fed{country.lower().replace(' ', '')}@anleague.com",
            "rating": random.randint(70, 85),
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "goalsFor": 0,
            "goalsAgainst": 0,
            "createdAt": datetime.utcnow()
        }
        result = db.federations.insert_one(federation)
        federation_ids.append(result.inserted_id)
        
        # Create 23 players for each federation
        positions = ["GK", "DF", "MD", "AT"]
        players = []
        
        # 3 Goalkeepers
        for j in range(3):
            player = create_player(country, "GK", j+1, result.inserted_id, is_captain=(j==0))
            players.append(player)
        
        # 8 Defenders
        for j in range(8):
            player = create_player(country, "DF", j+4, result.inserted_id)
            players.append(player)
        
        # 8 Midfielders
        for j in range(8):
            player = create_player(country, "MD", j+12, result.inserted_id)
            players.append(player)
        
        # 4 Attackers
        for j in range(4):
            player = create_player(country, "AT", j+20, result.inserted_id)
            players.append(player)
        
        db.players.insert_many(players)
        print(f"  ✅ Created {country} with 23 players")

    # Create tournament
    print("🏆 Creating tournament structure...")
    tournament = {
        "name": "African Nations League 2025",
        "edition": "First Edition",
        "status": "pending",  # pending, active, completed
        "currentRound": "quarterfinals",
        "registeredTeams": 7,
        "champion": None,
        "runnerUp": None,
        "startDate": datetime.utcnow() + timedelta(days=7),
        "endDate": datetime.utcnow() + timedelta(days=21),
        "createdAt": datetime.utcnow()
    }
    tournament_result = db.tournaments.insert_one(tournament)
    tournament_id = tournament_result.inserted_id

    # Create matches with proper bracket structure
    print("⚽ Creating tournament bracket...")
    matches = []
    
    # Quarter-finals (4 matches)
    match_dates = [
        datetime.utcnow() + timedelta(days=7),
        datetime.utcnow() + timedelta(days=8),
        datetime.utcnow() + timedelta(days=9),
        datetime.utcnow() + timedelta(days=10)
    ]
    
    for i in range(4):
        # Assign teams to matches - for demo, first 2 matches have teams
        if i < 2:
            teamA_id = federation_ids[i*2]
            teamB_id = federation_ids[i*2 + 1] if i*2 + 1 < len(federation_ids) else None
        else:
            teamA_id = None
            teamB_id = None
            
        match_data = {
            "tournamentId": tournament_id,
            "round": "quarterfinal",
            "matchNumber": i + 1,
            "teamA": teamA_id,
            "teamB": teamB_id,
            "scoreA": 0,
            "scoreB": 0,
            "winner": None,
            "status": "scheduled",
            "matchDate": match_dates[i],
            "stadium": f"Stadium {i+1}",
            "city": random.choice(["Cairo", "Johannesburg", "Lagos", "Casablanca", "Abidjan"]),
            "goals": [],
            "cards": [],
            "substitutions": [],
            "commentary": [],
            "simulationType": None,
            "createdAt": datetime.utcnow()
        }
        matches.append(match_data)

    # Semi-finals (2 matches)
    semi_dates = [datetime.utcnow() + timedelta(days=14), datetime.utcnow() + timedelta(days=15)]
    for i in range(2):
        match_data = {
            "tournamentId": tournament_id,
            "round": "semifinal",
            "matchNumber": i + 1,
            "teamA": None,  # Will be filled by quarter-final winners
            "teamB": None,
            "scoreA": 0,
            "scoreB": 0,
            "winner": None,
            "status": "scheduled",
            "matchDate": semi_dates[i],
            "stadium": "National Stadium",
            "city": "Cairo",
            "goals": [],
            "cards": [],
            "substitutions": [],
            "commentary": [],
            "simulationType": None,
            "createdAt": datetime.utcnow()
        }
        matches.append(match_data)

    # Final (1 match)
    match_data = {
        "tournamentId": tournament_id,
        "round": "final",
        "matchNumber": 1,
        "teamA": None,  # Will be filled by semi-final winners
        "teamB": None,
        "scoreA": 0,
        "scoreB": 0,
        "winner": None,
        "status": "scheduled",
        "matchDate": datetime.utcnow() + timedelta(days=21),
        "stadium": "Cairo International Stadium",
        "city": "Cairo",
        "goals": [],
        "cards": [],
        "substitutions": [],
        "commentary": [],
        "simulationType": None,
        "createdAt": datetime.utcnow()
    }
    matches.append(match_data)

    db.matches.insert_many(matches)

    # Create indexes for better performance
    print("📊 Creating database indexes...")
    db.federations.create_index("country", unique=True)
    db.players.create_index("federationId")
    db.matches.create_index([("tournamentId", 1), ("round", 1)])
    db.matches.create_index("status")
    db.users.create_index("email", unique=True)

    # Verify data creation
    fed_count = db.federations.count_documents({})
    player_count = db.players.count_documents({})
    match_count = db.matches.count_documents({})
    
    print("\n✅ Database initialized successfully!")
    print("📊 Summary:")
    print(f"   👥 Federations: {fed_count} teams")
    print(f"   ⚽ Players: {player_count} total players")
    print(f"   🏆 Matches: {match_count} matches in bracket")
    print(f"   👨‍💼 Admin users: 3 accounts created")
    print(f"   🔗 MongoDB Database: AfricanLeague")
    print("\n🎯 Ready for 8th team registration!")
    
    client.close()

def create_player(country, position, jersey_number, federation_id, is_captain=False):
    """Helper function to create a player with realistic data"""
    first_names = ["John", "David", "Mohamed", "Ahmed", "Kofi", "Kwame", "Ibrahim", "Samuel", "Joseph", "Michael"]
    last_names = ["Diallo", "Traore", "Mensah", "Appiah", "Ouedraogo", "Ndiaye", "Kamara", "Sarr", "Keita", "Cisse"]
    
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # Generate ratings - natural position gets 50-100, others get 0-50
    ratings = {}
    for pos in ["GK", "DF", "MD", "AT"]:
        if pos == position:
            ratings[pos] = random.randint(65, 90)  # Higher range for natural position
        else:
            ratings[pos] = random.randint(10, 45)  # Lower range for other positions
    
    return {
        "name": name,
        "country": country,
        "jerseyNumber": jersey_number,
        "naturalPosition": position,
        "ratings": ratings,
        "federationId": federation_id,
        "isCaptain": is_captain,
        "goals": 0,
        "assists": 0,
        "yellowCards": 0,
        "redCards": 0,
        "matchesPlayed": 0,
        "minutesPlayed": 0,
        "createdAt": datetime.utcnow()
    }

def add_8th_team(country_name):
    """Function to demonstrate adding the 8th team"""
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client['AfricanLeague']
    
    # Check if country already exists
    if db.federations.find_one({"country": country_name}):
        print(f"❌ {country_name} already exists!")
        return False
    
    # Create federation
    federation = {
        "country": country_name,
        "manager": f"Manager of {country_name}",
        "email": f"fed{country_name.lower().replace(' ', '')}@anleague.com",
        "rating": random.randint(70, 85),
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "goalsFor": 0,
        "goalsAgainst": 0,
        "createdAt": datetime.utcnow()
    }
    result = db.federations.insert_one(federation)
    
    # Create players
    players = []
    positions = ["GK", "DF", "MD", "AT"]
    
    # 3 Goalkeepers
    for j in range(3):
        player = create_player(country_name, "GK", j+1, result.inserted_id, is_captain=(j==0))
        players.append(player)
    
    # 8 Defenders
    for j in range(8):
        player = create_player(country_name, "DF", j+4, result.inserted_id)
        players.append(player)
    
    # 8 Midfielders
    for j in range(8):
        player = create_player(country_name, "MD", j+12, result.inserted_id)
        players.append(player)
    
    # 4 Attackers
    for j in range(4):
        player = create_player(country_name, "AT", j+20, result.inserted_id)
        players.append(player)
    
    db.players.insert_many(players)
    
    # Update tournament team count
    db.tournaments.update_one({}, {"$inc": {"registeredTeams": 1}})
    
    # Assign the 8th team to remaining quarter-final spots
    empty_matches = list(db.matches.find({
        "round": "quarterfinal", 
        "$or": [{"teamA": None}, {"teamB": None}]
    }))
    
    for match in empty_matches:
        if match.get('teamA') is None:
            db.matches.update_one({"_id": match['_id']}, {"$set": {"teamA": result.inserted_id}})
        elif match.get('teamB') is None:
            db.matches.update_one({"_id": match['_id']}, {"$set": {"teamB": result.inserted_id}})
    
    print(f"✅ Successfully added {country_name} as the 8th team!")
    print(f"📊 Tournament now has 8 teams - ready to start!")
    client.close()
    return True

if __name__ == "__main__":
    initialize_database()
    
    # Uncomment the line below to demonstrate adding the 8th team
    # add_8th_team("South Africa")