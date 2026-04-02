"""
Mock data generation service
"""
import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict

# Teams by sport
TEAMS = {
    "football": [
        ("Real Madrid", "Barcelona"), ("Manchester City", "Arsenal"),
        ("Bayern Munich", "Borussia Dortmund"), ("PSG", "Marseille"),
        ("Inter Milan", "AC Milan"), ("Juventus", "Napoli"),
        ("Liverpool", "Manchester United"), ("Chelsea", "Tottenham")
    ],
    "basketball": [
        ("Los Angeles Lakers", "Boston Celtics"), ("Golden State Warriors", "Phoenix Suns"),
        ("Milwaukee Bucks", "Miami Heat"), ("Denver Nuggets", "Memphis Grizzlies")
    ],
    "tennis": [
        ("Djokovic N.", "Alcaraz C."), ("Sinner J.", "Medvedev D."),
        ("Nadal R.", "Federer R."), ("Zverev A.", "Tsitsipas S.")
    ],
    "baseball": [
        ("New York Yankees", "Boston Red Sox"), ("Los Angeles Dodgers", "San Francisco Giants"),
        ("Houston Astros", "Texas Rangers"), ("Atlanta Braves", "New York Mets")
    ],
    "hockey": [
        ("Toronto Maple Leafs", "Montreal Canadiens"), ("Boston Bruins", "New York Rangers"),
        ("Vegas Golden Knights", "Colorado Avalanche"), ("Edmonton Oilers", "Calgary Flames")
    ],
    "mma": [
        ("Jon Jones", "Stipe Miocic"), ("Islam Makhachev", "Charles Oliveira"),
        ("Leon Edwards", "Kamaru Usman"), ("Alex Pereira", "Jiri Prochazka")
    ]
}

LEAGUES = {
    "football": ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Champions League"],
    "basketball": ["NBA", "EuroLeague"],
    "tennis": ["ATP Tour", "Grand Slam"],
    "baseball": ["MLB"],
    "hockey": ["NHL"],
    "mma": ["UFC"]
}

BOOKMAKERS = ["Bet365", "Pinnacle", "1xBet", "Betfair", "William Hill", "Unibet", "888sport", "Betway"]


def generate_mock_matches(count: int = 20, sport_filter: str = None, date_filter: str = None) -> List[Dict]:
    """Generate mock match data for demo mode"""
    matches = []
    sports = [sport_filter] if sport_filter and sport_filter in TEAMS else list(TEAMS.keys())
    
    # Date filtering
    now = datetime.now(timezone.utc)
    if date_filter == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif date_filter == "tomorrow":
        start_date = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif date_filter == "week":
        start_date = now
        end_date = now + timedelta(days=7)
    else:
        start_date = now
        end_date = now + timedelta(days=7)
    
    for i in range(count):
        sport = random.choice(sports)
        teams = random.choice(TEAMS.get(sport, TEAMS["football"]))
        league = random.choice(LEAGUES.get(sport, LEAGUES["football"]))
        
        # Random time within date range
        delta_hours = random.randint(1, int((end_date - start_date).total_seconds() / 3600))
        start_time = start_date + timedelta(hours=delta_hours)
        
        # Generate odds from multiple bookmakers
        base_home = random.uniform(1.5, 4.0)
        base_draw = random.uniform(2.8, 4.5) if sport == "football" else None
        base_away = random.uniform(1.5, 4.0)
        
        odds = {}
        for bookmaker in random.sample(BOOKMAKERS, random.randint(4, 7)):
            bookmaker_odds = {
                "home": round(base_home * random.uniform(0.95, 1.05), 2),
                "away": round(base_away * random.uniform(0.95, 1.05), 2)
            }
            if base_draw:
                bookmaker_odds["draw"] = round(base_draw * random.uniform(0.95, 1.05), 2)
            odds[bookmaker] = bookmaker_odds
        
        match = {
            "id": str(uuid.uuid4()),
            "sport": sport,
            "league": league,
            "home_team": teams[0],
            "away_team": teams[1],
            "start_time": start_time.isoformat(),
            "status": "upcoming",
            "home_score": None,
            "away_score": None,
            "odds": odds,
            "stats": None,
            "is_real_data": False
        }
        matches.append(match)
    
    # Sort by start time
    matches.sort(key=lambda x: x["start_time"])
    return matches
