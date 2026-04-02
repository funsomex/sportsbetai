"""
Application configuration and environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB Configuration
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'sportsbetai')

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'sportsbetai_jwt_secret')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# AI/LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# The Odds API Configuration
THE_ODDS_API_KEY = os.environ.get('THE_ODDS_API_KEY')
THE_ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# Cache Configuration
CACHE_TTL_MINUTES = 60

# Sports mapping for The Odds API
ODDS_API_SPORTS = {
    "football": ["soccer_spain_la_liga", "soccer_epl", "soccer_italy_serie_a", "soccer_germany_bundesliga", "soccer_france_ligue_one", "soccer_uefa_champs_league"],
    "basketball": ["basketball_nba", "basketball_euroleague"],
    "tennis": ["tennis_atp_aus_open", "tennis_atp_french_open", "tennis_atp_wimbledon", "tennis_atp_us_open"],
    "baseball": ["baseball_mlb"],
    "hockey": ["icehockey_nhl"],
    "mma": ["mma_mixed_martial_arts"],
    "esports": ["esports_lol", "esports_csgo", "esports_dota2"]
}

SPORT_DISPLAY_NAMES = {
    "soccer_spain_la_liga": "La Liga",
    "soccer_epl": "Premier League", 
    "soccer_italy_serie_a": "Serie A",
    "soccer_germany_bundesliga": "Bundesliga",
    "soccer_france_ligue_one": "Ligue 1",
    "soccer_uefa_champs_league": "Champions League",
    "basketball_nba": "NBA",
    "basketball_euroleague": "EuroLeague",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "mma_mixed_martial_arts": "MMA/UFC",
    "esports_lol": "League of Legends",
    "esports_csgo": "CS2",
    "esports_dota2": "Dota 2"
}

# Sport categories for filtering
SPORT_CATEGORIES = {
    "soccer": "football",
    "football": "football",
    "basketball": "basketball",
    "tennis": "tennis",
    "baseball": "baseball",
    "hockey": "hockey",
    "mma": "mma",
    "esports": "esports"
}
