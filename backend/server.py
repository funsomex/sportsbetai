from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import random
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'sportsbetai_jwt_secret')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Telegram Config
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# The Odds API Config
THE_ODDS_API_KEY = os.environ.get('THE_ODDS_API_KEY')
THE_ODDS_API_BASE = "https://api.the-odds-api.com/v4"

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

# Create the main app
app = FastAPI(title="SportsBetAI", description="Sistema Predictivo de Apuestas Deportivas con IA")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== MODELS ==============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    telegram_chat_id: Optional[str] = None
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TelegramSetup(BaseModel):
    chat_id: str

class Match(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    start_time: str
    status: str  # "upcoming", "live", "finished"
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    odds: Dict[str, Dict[str, float]]  # bookmaker -> market -> odds
    stats: Optional[Dict[str, Any]] = None

class ValueBet(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    match_id: str
    match: Dict[str, Any]
    market: str
    selection: str
    bookmaker: str
    odds: float
    true_probability: float
    implied_probability: float
    value_percentage: float
    confidence: float
    ai_analysis: Optional[str] = None
    created_at: str

class Parlay(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    name: str
    selections: List[Dict[str, Any]]
    total_odds: float
    stake: Optional[float] = None
    potential_profit: Optional[float] = None
    status: str  # "active", "won", "lost", "partial"
    created_at: str

class PredictionHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    match_id: str
    prediction_type: str
    selection: str
    odds: float
    stake: float
    result: Optional[str] = None  # "won", "lost", "pending"
    profit: Optional[float] = None
    created_at: str

class AIAnalysisRequest(BaseModel):
    match_id: str
    analysis_type: str = "general"

class ParlayCreate(BaseModel):
    selections: List[Dict[str, Any]]
    name: str = "Mi Combinada"
    stake: Optional[float] = None

class PredictionCreate(BaseModel):
    match_id: str
    prediction_type: str
    selection: str
    odds: float
    stake: float = 0

# ============== AUTH FUNCTIONS ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============== REAL DATA FROM THE ODDS API ==============

async def fetch_real_sports():
    """Fetch available sports from The Odds API"""
    if not THE_ODDS_API_KEY:
        return []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{THE_ODDS_API_BASE}/sports",
                params={"apiKey": THE_ODDS_API_KEY}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logger.error(f"Error fetching sports: {e}")
    return []

async def fetch_real_odds(sport_key: str, regions: str = "eu,us", markets: str = "h2h"):
    """Fetch real odds from The Odds API"""
    if not THE_ODDS_API_KEY:
        return []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{THE_ODDS_API_BASE}/sports/{sport_key}/odds",
                params={
                    "apiKey": THE_ODDS_API_KEY,
                    "regions": regions,
                    "markets": markets,
                    "oddsFormat": "decimal"
                },
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Odds API returned {response.status_code} for {sport_key}")
    except Exception as e:
        logger.error(f"Error fetching odds for {sport_key}: {e}")
    return []

async def get_all_real_matches(sport_filter: str = None) -> List[Dict]:
    """Get all real matches with odds from multiple sports"""
    all_matches = []
    
    # Determine which sports to fetch
    if sport_filter and sport_filter in ODDS_API_SPORTS:
        sports_to_fetch = ODDS_API_SPORTS[sport_filter]
    else:
        # Fetch main sports
        sports_to_fetch = [
            "soccer_spain_la_liga", "soccer_epl", "soccer_italy_serie_a",
            "basketball_nba", "baseball_mlb", "icehockey_nhl", "mma_mixed_martial_arts"
        ]
    
    for sport_key in sports_to_fetch:
        try:
            odds_data = await fetch_real_odds(sport_key)
            for event in odds_data:
                # Convert to our match format
                odds_by_bookmaker = {}
                for bookmaker in event.get("bookmakers", []):
                    bookmaker_name = bookmaker.get("title", bookmaker.get("key"))
                    markets = {}
                    for market in bookmaker.get("markets", []):
                        if market.get("key") == "h2h":
                            for outcome in market.get("outcomes", []):
                                name = outcome.get("name")
                                price = outcome.get("price")
                                if name == event.get("home_team"):
                                    markets["home"] = price
                                elif name == event.get("away_team"):
                                    markets["away"] = price
                                elif name.lower() == "draw":
                                    markets["draw"] = price
                    if markets:
                        odds_by_bookmaker[bookmaker_name] = markets
                
                # Determine sport type from sport_key
                sport_type = "football"
                if "basketball" in sport_key:
                    sport_type = "basketball"
                elif "baseball" in sport_key:
                    sport_type = "baseball"
                elif "hockey" in sport_key or "icehockey" in sport_key:
                    sport_type = "hockey"
                elif "mma" in sport_key:
                    sport_type = "mma"
                elif "tennis" in sport_key:
                    sport_type = "tennis"
                elif "esports" in sport_key:
                    sport_type = "esports"
                
                match = {
                    "id": event.get("id"),
                    "sport": sport_type,
                    "league": SPORT_DISPLAY_NAMES.get(sport_key, event.get("sport_title", sport_key)),
                    "home_team": event.get("home_team"),
                    "away_team": event.get("away_team"),
                    "start_time": event.get("commence_time"),
                    "status": "upcoming",  # The Odds API mainly provides upcoming matches
                    "home_score": None,
                    "away_score": None,
                    "odds": odds_by_bookmaker,
                    "stats": None,
                    "is_real_data": True
                }
                all_matches.append(match)
        except Exception as e:
            logger.error(f"Error processing {sport_key}: {e}")
            continue
    
    # Sort by start time
    all_matches.sort(key=lambda x: x.get("start_time", ""))
    return all_matches

def calculate_real_value_bets(matches: List[Dict]) -> List[Dict]:
    """Calculate value bets from real odds data"""
    value_bets = []
    
    for match in matches:
        if not match.get("odds"):
            continue
        
        # Find best odds across all bookmakers for each outcome
        best_odds = {"home": 0, "draw": 0, "away": 0}
        best_bookmaker = {"home": "", "draw": "", "away": ""}
        all_odds = {"home": [], "draw": [], "away": []}
        
        for bookmaker, odds in match["odds"].items():
            for market in ["home", "draw", "away"]:
                if market in odds:
                    all_odds[market].append(odds[market])
                    if odds[market] > best_odds[market]:
                        best_odds[market] = odds[market]
                        best_bookmaker[market] = bookmaker
        
        # Calculate implied probabilities and find value
        for market in ["home", "draw", "away"]:
            if best_odds[market] > 0 and len(all_odds[market]) >= 2:
                # Average implied probability from all bookmakers
                avg_implied_prob = sum(1/o for o in all_odds[market]) / len(all_odds[market])
                
                # Best odds implied probability
                best_implied_prob = 1 / best_odds[market]
                
                # Value = difference between average market view and best available odds
                # If best odds offer lower implied prob than market average, there's value
                value_percentage = ((avg_implied_prob / best_implied_prob) - 1) * 100
                
                # Also consider odds deviation for confidence
                odds_std = (max(all_odds[market]) - min(all_odds[market])) / min(all_odds[market]) * 100
                confidence = max(50, min(95, 85 - odds_std))  # Higher deviation = lower confidence
                
                if value_percentage > 2:  # Minimum 2% value
                    selection = match["home_team"] if market == "home" else (match["away_team"] if market == "away" else "Empate")
                    
                    value_bet = {
                        "id": str(uuid.uuid4()),
                        "match_id": match["id"],
                        "match": {
                            "home_team": match["home_team"],
                            "away_team": match["away_team"],
                            "league": match["league"],
                            "sport": match["sport"],
                            "start_time": match["start_time"]
                        },
                        "market": market,
                        "selection": selection,
                        "bookmaker": best_bookmaker[market],
                        "odds": best_odds[market],
                        "true_probability": round(avg_implied_prob * 100, 1),
                        "implied_probability": round(best_implied_prob * 100, 1),
                        "value_percentage": round(value_percentage, 1),
                        "confidence": round(confidence, 1),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "is_real_data": True
                    }
                    value_bets.append(value_bet)
    
    # Sort by value percentage
    value_bets.sort(key=lambda x: x["value_percentage"], reverse=True)
    return value_bets[:20]

# ============== MOCK DATA GENERATORS ==============

SPORTS = ["football", "basketball", "tennis", "baseball", "hockey", "mma", "esports"]
BOOKMAKERS = ["BetPlay", "Bet365", "1xBet", "Pinnacle", "Betfair"]

LEAGUES = {
    "football": ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Champions League"],
    "basketball": ["NBA", "EuroLeague", "ACB", "NBL"],
    "tennis": ["ATP Tour", "WTA Tour", "Grand Slam"],
    "baseball": ["MLB", "NPB", "KBO"],
    "hockey": ["NHL", "KHL", "SHL"],
    "mma": ["UFC", "Bellator", "ONE Championship"],
    "esports": ["League of Legends", "CS2", "Dota 2", "Valorant"]
}

TEAMS = {
    "football": {
        "Premier League": [("Manchester City", "Arsenal"), ("Liverpool", "Chelsea"), ("Manchester United", "Newcastle"), ("Tottenham", "Aston Villa")],
        "La Liga": [("Real Madrid", "Barcelona"), ("Atletico Madrid", "Sevilla"), ("Real Sociedad", "Athletic Bilbao")],
        "Serie A": [("Inter Milan", "AC Milan"), ("Juventus", "Napoli"), ("Roma", "Lazio")],
        "Bundesliga": [("Bayern Munich", "Borussia Dortmund"), ("RB Leipzig", "Bayer Leverkusen")],
        "Champions League": [("Real Madrid", "Manchester City"), ("Bayern Munich", "Barcelona"), ("PSG", "Inter Milan")]
    },
    "basketball": {
        "NBA": [("Lakers", "Celtics"), ("Warriors", "Heat"), ("Nuggets", "76ers"), ("Bucks", "Suns")],
        "EuroLeague": [("Real Madrid", "Barcelona"), ("Olympiacos", "Fenerbahce")]
    },
    "tennis": {
        "ATP Tour": [("Djokovic N.", "Alcaraz C."), ("Sinner J.", "Medvedev D."), ("Zverev A.", "Rublev A.")],
        "WTA Tour": [("Swiatek I.", "Sabalenka A."), ("Gauff C.", "Rybakina E.")]
    },
    "mma": {
        "UFC": [("Jon Jones", "Tom Aspinall"), ("Islam Makhachev", "Dustin Poirier"), ("Alex Pereira", "Jamahal Hill")]
    },
    "esports": {
        "League of Legends": [("T1", "Gen.G"), ("JDG", "BLG"), ("G2", "Fnatic")],
        "CS2": [("NAVI", "FaZe"), ("Vitality", "G2"), ("Spirit", "Cloud9")]
    }
}

def generate_odds() -> Dict[str, Dict[str, float]]:
    base_home = random.uniform(1.4, 3.5)
    base_draw = random.uniform(2.8, 4.2)
    base_away = random.uniform(1.6, 4.0)
    
    odds = {}
    for bookmaker in BOOKMAKERS:
        variation = random.uniform(-0.15, 0.15)
        odds[bookmaker] = {
            "home": round(base_home + variation + random.uniform(-0.1, 0.1), 2),
            "draw": round(base_draw + variation + random.uniform(-0.1, 0.1), 2),
            "away": round(base_away + variation + random.uniform(-0.1, 0.1), 2),
            "over_2.5": round(random.uniform(1.6, 2.4), 2),
            "under_2.5": round(random.uniform(1.5, 2.3), 2),
            "btts_yes": round(random.uniform(1.5, 2.2), 2),
            "btts_no": round(random.uniform(1.6, 2.4), 2)
        }
    return odds

def generate_match_stats() -> Dict[str, Any]:
    return {
        "home": {
            "possession": random.randint(35, 65),
            "shots": random.randint(5, 20),
            "shots_on_target": random.randint(2, 10),
            "corners": random.randint(2, 12),
            "fouls": random.randint(5, 18),
            "xG": round(random.uniform(0.5, 3.5), 2),
            "form": [random.choice(["W", "D", "L"]) for _ in range(5)]
        },
        "away": {
            "possession": 0,  # Will be calculated
            "shots": random.randint(5, 18),
            "shots_on_target": random.randint(1, 8),
            "corners": random.randint(1, 10),
            "fouls": random.randint(6, 20),
            "xG": round(random.uniform(0.3, 2.8), 2),
            "form": [random.choice(["W", "D", "L"]) for _ in range(5)]
        }
    }

def generate_mock_matches(sport: str = None, count: int = 20) -> List[Dict]:
    matches = []
    sports_to_generate = [sport] if sport else SPORTS
    
    for s in sports_to_generate:
        leagues = LEAGUES.get(s, [])
        for league in leagues[:2]:
            teams_list = TEAMS.get(s, {}).get(league, [])
            if not teams_list:
                continue
            for home, away in teams_list[:3]:
                status = random.choice(["upcoming", "live", "finished"])
                match_time = datetime.now(timezone.utc) + timedelta(hours=random.randint(-2, 48))
                
                stats = generate_match_stats()
                stats["away"]["possession"] = 100 - stats["home"]["possession"]
                
                match = {
                    "id": str(uuid.uuid4()),
                    "sport": s,
                    "league": league,
                    "home_team": home,
                    "away_team": away,
                    "start_time": match_time.isoformat(),
                    "status": status,
                    "home_score": random.randint(0, 4) if status in ["live", "finished"] else None,
                    "away_score": random.randint(0, 3) if status in ["live", "finished"] else None,
                    "odds": generate_odds(),
                    "stats": stats
                }
                matches.append(match)
    
    return matches[:count]

def calculate_value_bets(matches: List[Dict]) -> List[Dict]:
    value_bets = []
    
    for match in matches:
        if match["status"] == "finished":
            continue
            
        for bookmaker, odds in match["odds"].items():
            for market, odd_value in odds.items():
                if market in ["home", "draw", "away"]:
                    # Simulated true probability calculation
                    implied_prob = 1 / odd_value
                    true_prob = implied_prob + random.uniform(-0.1, 0.15)
                    true_prob = max(0.1, min(0.9, true_prob))
                    
                    value_percentage = ((true_prob * odd_value) - 1) * 100
                    
                    if value_percentage > 3:  # Value bet threshold
                        value_bet = {
                            "id": str(uuid.uuid4()),
                            "match_id": match["id"],
                            "match": {
                                "home_team": match["home_team"],
                                "away_team": match["away_team"],
                                "league": match["league"],
                                "sport": match["sport"],
                                "start_time": match["start_time"]
                            },
                            "market": market,
                            "selection": match["home_team"] if market == "home" else (match["away_team"] if market == "away" else "Draw"),
                            "bookmaker": bookmaker,
                            "odds": odd_value,
                            "true_probability": round(true_prob * 100, 1),
                            "implied_probability": round(implied_prob * 100, 1),
                            "value_percentage": round(value_percentage, 1),
                            "confidence": round(random.uniform(60, 95), 1),
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                        value_bets.append(value_bet)
    
    # Sort by value percentage and return top ones
    value_bets.sort(key=lambda x: x["value_percentage"], reverse=True)
    return value_bets[:15]

# ============== AUTH ENDPOINTS ==============

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    try:
        existing = await db.users.find_one({"email": user_data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Este email ya está registrado")
        
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "password": hash_password(user_data.password),
            "telegram_chat_id": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_doc)
        
        token = create_token(user_id)
        user_response = UserResponse(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            created_at=user_doc["created_at"]
        )
        return TokenResponse(access_token=token, user=user_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos. Por favor intenta más tarde.")

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    try:
        user = await db.users.find_one({"email": credentials.email})
        if not user or not verify_password(credentials.password, user["password"]):
            raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
        
        token = create_token(user["id"])
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            telegram_chat_id=user.get("telegram_chat_id"),
            created_at=user["created_at"]
        )
        return TokenResponse(access_token=token, user=user_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos. Por favor intenta más tarde.")

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str

@api_router.post("/auth/forgot-password")
async def forgot_password(data: PasswordResetRequest):
    """Solicitar recuperación de contraseña"""
    try:
        user = await db.users.find_one({"email": data.email})
        if not user:
            # Por seguridad, no revelamos si el email existe o no
            return {"message": "Si el email está registrado, recibirás instrucciones para recuperar tu contraseña"}
        
        # Generar código de 6 dígitos
        reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Guardar el código en la base de datos
        await db.password_resets.update_one(
            {"email": data.email},
            {"$set": {
                "email": data.email,
                "code": reset_code,
                "expires_at": expiry.isoformat(),
                "used": False
            }},
            upsert=True
        )
        
        # Intentar enviar por Telegram si el usuario tiene configurado
        telegram_sent = False
        if user.get("telegram_chat_id") and TELEGRAM_BOT_TOKEN:
            try:
                async with httpx.AsyncClient() as client:
                    message = f"🔐 *Recuperación de Contraseña*\n\nTu código de recuperación es:\n\n`{reset_code}`\n\nEste código expira en 15 minutos."
                    await client.post(
                        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": user["telegram_chat_id"],
                            "text": message,
                            "parse_mode": "Markdown"
                        }
                    )
                    telegram_sent = True
            except Exception as e:
                logger.error(f"Error enviando código por Telegram: {e}")
        
        response_msg = "Si el email está registrado, recibirás instrucciones para recuperar tu contraseña"
        if telegram_sent:
            response_msg = "Te hemos enviado un código de recuperación por Telegram"
        
        # Para desarrollo, también devolvemos el código (quitar en producción real)
        return {"message": response_msg, "debug_code": reset_code}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en forgot-password: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")

@api_router.post("/auth/reset-password")
async def reset_password(data: PasswordResetConfirm):
    """Confirmar el cambio de contraseña con el código"""
    try:
        # Buscar el código de reset
        reset_record = await db.password_resets.find_one({
            "email": data.email,
            "code": data.reset_code,
            "used": False
        })
        
        if not reset_record:
            raise HTTPException(status_code=400, detail="Código inválido o expirado")
        
        # Verificar expiración
        expires_at = datetime.fromisoformat(reset_record["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="El código ha expirado")
        
        # Actualizar contraseña
        new_hashed = hash_password(data.new_password)
        await db.users.update_one(
            {"email": data.email},
            {"$set": {"password": new_hashed}}
        )
        
        # Marcar código como usado
        await db.password_resets.update_one(
            {"_id": reset_record["_id"]},
            {"$set": {"used": True}}
        )
        
        return {"message": "Contraseña actualizada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reset-password: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al cambiar la contraseña")

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

# ============== TELEGRAM ENDPOINTS ==============

@api_router.post("/telegram/setup")
async def setup_telegram(data: TelegramSetup, current_user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"telegram_chat_id": data.chat_id}}
    )
    return {"message": "Telegram configurado correctamente", "chat_id": data.chat_id}

@api_router.post("/telegram/test")
async def test_telegram(current_user: dict = Depends(get_current_user)):
    chat_id = current_user.get("telegram_chat_id")
    if not chat_id:
        raise HTTPException(status_code=400, detail="Telegram no configurado")
    
    try:
        async with httpx.AsyncClient() as client:
            message = f"🎯 *SportsBetAI*\n\n✅ ¡Conexión exitosa!\n\nHola {current_user['name']}, las alertas de value bets llegarán a este chat."
            response = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Error enviando mensaje a Telegram")
        return {"message": "Mensaje de prueba enviado"}
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/telegram/send-alert")
async def send_telegram_alert(value_bet: dict, current_user: dict = Depends(get_current_user)):
    chat_id = current_user.get("telegram_chat_id")
    if not chat_id:
        raise HTTPException(status_code=400, detail="Telegram no configurado")
    
    try:
        message = f"""
🎯 *VALUE BET DETECTADO*

⚽ *{value_bet['match']['home_team']} vs {value_bet['match']['away_team']}*
🏆 {value_bet['match']['league']}

📊 *Selección:* {value_bet['selection']}
💰 *Cuota:* {value_bet['odds']}
📈 *Valor:* +{value_bet['value_percentage']}%
🎯 *Confianza:* {value_bet['confidence']}%

🏠 Casa: {value_bet['bookmaker']}
        """
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
        return {"message": "Alerta enviada"}
    except Exception as e:
        logger.error(f"Telegram alert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== MATCHES ENDPOINTS ==============

@api_router.get("/matches")
async def get_matches(sport: str = None, status: str = None, limit: int = 20):
    """Get matches - uses real data from The Odds API if available"""
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches(sport)
            if status:
                matches = [m for m in matches if m["status"] == status]
            return {"matches": matches[:limit], "total": len(matches), "source": "real"}
        except Exception as e:
            logger.error(f"Error fetching real matches: {e}")
    
    # Fallback to mock data
    matches = generate_mock_matches(sport, limit)
    if status:
        matches = [m for m in matches if m["status"] == status]
    return {"matches": matches, "total": len(matches), "source": "mock"}

@api_router.get("/matches/{match_id}")
async def get_match(match_id: str):
    """Get single match by ID"""
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches()
            for m in matches:
                if m["id"] == match_id:
                    return m
        except Exception as e:
            logger.error(f"Error fetching match: {e}")
    
    # Fallback to mock
    match = generate_mock_matches(count=1)[0]
    match["id"] = match_id
    return match

@api_router.get("/matches/live")
async def get_live_matches():
    """Get live matches"""
    matches = generate_mock_matches(count=30)
    live = [m for m in matches if m["status"] == "live"]
    return {"matches": live, "total": len(live)}

# ============== VALUE BETS ENDPOINTS ==============

@api_router.get("/value-bets")
async def get_value_bets(sport: str = None, min_value: float = 2.0):
    """Get value bets - uses real odds data if available"""
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches(sport)
            value_bets = calculate_real_value_bets(matches)
            filtered = [vb for vb in value_bets if vb["value_percentage"] >= min_value]
            return {"value_bets": filtered, "total": len(filtered), "source": "real"}
        except Exception as e:
            logger.error(f"Error calculating real value bets: {e}")
    
    # Fallback to mock
    matches = generate_mock_matches(sport, count=30)
    value_bets = calculate_value_bets(matches)
    filtered = [vb for vb in value_bets if vb["value_percentage"] >= min_value]
    return {"value_bets": filtered, "total": len(filtered), "source": "mock"}

@api_router.get("/value-bets/top")
async def get_top_value_bets(limit: int = 5):
    """Get top value bets"""
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches()
            value_bets = calculate_real_value_bets(matches)
            return {"value_bets": value_bets[:limit], "source": "real"}
        except Exception as e:
            logger.error(f"Error getting top value bets: {e}")
    
    # Fallback to mock
    matches = generate_mock_matches(count=50)
    value_bets = calculate_value_bets(matches)
    return {"value_bets": value_bets[:limit], "source": "mock"}

# ============== ODDS COMPARISON ==============

@api_router.get("/odds/compare/{match_id}")
async def compare_odds(match_id: str):
    """Compare odds across bookmakers for a specific match"""
    match = None
    
    # Try to find real match first
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches()
            for m in matches:
                if m["id"] == match_id:
                    match = m
                    break
        except Exception as e:
            logger.error(f"Error finding match for comparison: {e}")
    
    # Fallback to mock
    if not match:
        match = generate_mock_matches(count=1)[0]
        match["id"] = match_id
    
    comparison = {
        "match": {
            "id": match["id"],
            "home_team": match["home_team"],
            "away_team": match["away_team"],
            "league": match["league"],
            "start_time": match["start_time"]
        },
        "odds_comparison": match["odds"],
        "best_odds": {
            "home": {"bookmaker": "", "odds": 0},
            "draw": {"bookmaker": "", "odds": 0},
            "away": {"bookmaker": "", "odds": 0}
        },
        "is_real_data": match.get("is_real_data", False)
    }
    
    for market in ["home", "draw", "away"]:
        best_odds = 0
        best_bookmaker = ""
        for bookmaker, odds in match["odds"].items():
            if market in odds and odds[market] > best_odds:
                best_odds = odds[market]
                best_bookmaker = bookmaker
        comparison["best_odds"][market] = {"bookmaker": best_bookmaker, "odds": best_odds}
    
    return comparison

@api_router.get("/odds/all")
async def get_all_odds():
    """Get all available odds from real API"""
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches()
            return {"matches": matches, "total": len(matches), "source": "real"}
        except Exception as e:
            logger.error(f"Error fetching all odds: {e}")
    
    return {"matches": [], "total": 0, "source": "none", "message": "API key not configured"}

# ============== AUTO PARLAY GENERATOR ==============

def generate_selection_analysis(selection, opponent, market, best_odds, best_bookmaker, 
                                worst_odds, avg_odds, all_bookmakers, confidence, 
                                value, league, sport) -> dict:
    """Generate detailed analysis explaining why this selection was chosen"""
    
    # Calculate key metrics
    implied_prob = round((1 / best_odds) * 100, 1)
    avg_implied_prob = round((1 / avg_odds) * 100, 1)
    odds_advantage = round(((best_odds / avg_odds) - 1) * 100, 1)
    num_bookmakers = len(all_bookmakers)
    
    # Determine position type
    position = "local" if market == "home" else "visitante"
    
    # Generate reasoning points
    reasons = []
    
    # Reason 1: Odds advantage
    if odds_advantage > 2:
        reasons.append(f"{best_bookmaker} ofrece cuota {best_odds:.2f}, un {odds_advantage}% superior al promedio del mercado ({avg_odds:.2f})")
    else:
        reasons.append(f"Cuota competitiva de {best_odds:.2f} en {best_bookmaker}")
    
    # Reason 2: Market consensus
    if confidence > 75:
        reasons.append(f"Alta consistencia entre {num_bookmakers} casas de apuestas indica mercado estable")
    elif confidence > 60:
        reasons.append(f"Consenso moderado entre {num_bookmakers} casas de apuestas")
    else:
        reasons.append(f"Variación en cuotas entre casas puede indicar oportunidad de valor")
    
    # Reason 3: Value analysis
    if value > 5:
        reasons.append(f"Value bet detectado: {value:.1f}% de valor sobre probabilidad implícita del mercado")
    elif value > 2:
        reasons.append(f"Ligero valor positivo detectado ({value:.1f}%)")
    
    # Reason 4: Position advantage (if home)
    if market == "home":
        reasons.append(f"{selection} juega como local, factor que históricamente favorece al equipo de casa")
    
    # Generate summary
    if confidence > 70 and value > 3:
        summary = f"Selección sólida con buena relación riesgo/recompensa"
    elif confidence > 60:
        summary = f"Opción equilibrada para diversificar la combinada"
    else:
        summary = f"Selección con potencial de valor, riesgo moderado"
    
    # Odds comparison table
    sorted_bookmakers = sorted(all_bookmakers.items(), key=lambda x: x[1], reverse=True)
    odds_comparison = [{"bookmaker": b, "odds": o} for b, o in sorted_bookmakers[:5]]
    
    return {
        "summary": summary,
        "reasons": reasons,
        "metrics": {
            "implied_probability": implied_prob,
            "market_avg_probability": avg_implied_prob,
            "odds_advantage_pct": odds_advantage,
            "value_pct": round(value, 1),
            "confidence_pct": round(confidence, 1),
            "bookmakers_analyzed": num_bookmakers
        },
        "odds_comparison": odds_comparison,
        "best_bookmaker": best_bookmaker,
        "recommendation": f"Apostar en {best_bookmaker} para obtener la mejor cuota disponible"
    }

class AutoParlayRequest(BaseModel):
    num_selections: int = 3  # Number of matches to include
    sports: List[str] = []  # Filter by sports (empty = all)
    min_odds: float = 1.20  # Minimum odds per selection
    max_odds: float = 2.50  # Maximum odds per selection
    target_total_odds: float = None  # Target combined odds (optional)
    risk_level: str = "medium"  # low, medium, high
    stake: float = None  # Amount to bet
    date_filter: str = "all"  # "today", "tomorrow", "week", "all", or specific date "YYYY-MM-DD"

@api_router.post("/parlays/generate")
async def generate_auto_parlay(request: AutoParlayRequest):
    """
    Genera combinadas automáticamente basadas en análisis de value bets y cuotas reales
    """
    try:
        # Get real matches
        matches = await get_all_real_matches()
        if not matches:
            raise HTTPException(status_code=404, detail="No hay partidos disponibles")
        
        # Filter by date
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        tomorrow_end = today_start + timedelta(days=2)
        week_end = today_start + timedelta(days=7)
        
        if request.date_filter == "today":
            matches = [m for m in matches if m.get("start_time") and 
                      today_start <= datetime.fromisoformat(m["start_time"].replace("Z", "+00:00")) < today_end]
        elif request.date_filter == "tomorrow":
            matches = [m for m in matches if m.get("start_time") and 
                      today_end <= datetime.fromisoformat(m["start_time"].replace("Z", "+00:00")) < tomorrow_end]
        elif request.date_filter == "week":
            matches = [m for m in matches if m.get("start_time") and 
                      today_start <= datetime.fromisoformat(m["start_time"].replace("Z", "+00:00")) < week_end]
        elif request.date_filter and request.date_filter not in ["all", ""]:
            # Specific date in YYYY-MM-DD format
            try:
                target_date = datetime.strptime(request.date_filter, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                target_end = target_date + timedelta(days=1)
                matches = [m for m in matches if m.get("start_time") and 
                          target_date <= datetime.fromisoformat(m["start_time"].replace("Z", "+00:00")) < target_end]
            except ValueError:
                pass  # Invalid date format, don't filter
        
        if not matches:
            date_msg = {
                "today": "hoy",
                "tomorrow": "mañana",
                "week": "esta semana"
            }.get(request.date_filter, request.date_filter)
            raise HTTPException(status_code=404, detail=f"No hay partidos disponibles para {date_msg}")
        
        # Filter by sports if specified
        if request.sports:
            sport_map = {
                "futbol": "football", "fútbol": "football", "football": "football", "soccer": "football",
                "baloncesto": "basketball", "basketball": "basketball", "nba": "basketball",
                "beisbol": "baseball", "béisbol": "baseball", "baseball": "baseball", "mlb": "baseball",
                "hockey": "hockey", "nhl": "hockey",
                "mma": "mma", "ufc": "mma",
                "tenis": "tennis", "tennis": "tennis"
            }
            allowed_sports = [sport_map.get(s.lower(), s.lower()) for s in request.sports]
            matches = [m for m in matches if m.get("sport", "").lower() in allowed_sports]
        
        if not matches:
            raise HTTPException(status_code=404, detail="No hay partidos para los deportes seleccionados")
        
        # Risk level configurations
        risk_configs = {
            "low": {"min_odds": 1.15, "max_odds": 1.60, "confidence_min": 75},
            "medium": {"min_odds": 1.40, "max_odds": 2.20, "confidence_min": 60},
            "high": {"min_odds": 1.80, "max_odds": 3.50, "confidence_min": 45}
        }
        config = risk_configs.get(request.risk_level, risk_configs["medium"])
        
        # Override with user preferences if provided
        min_odds = request.min_odds or config["min_odds"]
        max_odds = request.max_odds or config["max_odds"]
        
        # Analyze each match and find best selections
        candidates = []
        for match in matches:
            if not match.get("odds"):
                continue
            
            # Find best odds for each outcome
            for market in ["home", "away"]:
                best_odds = 0
                best_bookmaker = ""
                worst_odds = float('inf')
                worst_bookmaker = ""
                all_odds = []
                all_bookmakers = {}
                
                for bookmaker, odds in match["odds"].items():
                    if market in odds and odds[market] > 0:
                        all_odds.append(odds[market])
                        all_bookmakers[bookmaker] = odds[market]
                        if odds[market] > best_odds:
                            best_odds = odds[market]
                            best_bookmaker = bookmaker
                        if odds[market] < worst_odds:
                            worst_odds = odds[market]
                            worst_bookmaker = bookmaker
                
                if best_odds < min_odds or best_odds > max_odds:
                    continue
                
                if len(all_odds) < 2:
                    continue
                
                # Calculate confidence based on odds consistency
                avg_odds = sum(all_odds) / len(all_odds)
                odds_spread = (max(all_odds) - min(all_odds)) / min(all_odds) * 100
                
                # Higher confidence if odds are consistent across bookmakers
                confidence = max(40, min(95, 85 - odds_spread))
                
                # Calculate implied value
                avg_implied = 1 / avg_odds
                best_implied = 1 / best_odds
                value = ((avg_implied / best_implied) - 1) * 100
                
                selection_name = match["home_team"] if market == "home" else match["away_team"]
                opponent_name = match["away_team"] if market == "home" else match["home_team"]
                
                # Score for ranking (combines value, confidence, and odds attractiveness)
                score = (value * 0.4) + (confidence * 0.4) + ((best_odds - 1) * 10 * 0.2)
                
                # Generate detailed analysis
                analysis = generate_selection_analysis(
                    selection=selection_name,
                    opponent=opponent_name,
                    market=market,
                    best_odds=best_odds,
                    best_bookmaker=best_bookmaker,
                    worst_odds=worst_odds,
                    avg_odds=avg_odds,
                    all_bookmakers=all_bookmakers,
                    confidence=confidence,
                    value=value,
                    league=match["league"],
                    sport=match["sport"]
                )
                
                candidates.append({
                    "match_id": match["id"],
                    "match": f"{match['home_team']} vs {match['away_team']}",
                    "home_team": match["home_team"],
                    "away_team": match["away_team"],
                    "league": match["league"],
                    "sport": match["sport"],
                    "start_time": match["start_time"],
                    "market": market,
                    "selection": selection_name,
                    "odds": best_odds,
                    "bookmaker": best_bookmaker,
                    "confidence": round(confidence, 1),
                    "value": round(value, 1),
                    "score": round(score, 2),
                    "analysis": analysis
                })
        
        if len(candidates) < request.num_selections:
            raise HTTPException(
                status_code=400, 
                detail=f"Solo hay {len(candidates)} selecciones válidas. Ajusta los filtros."
            )
        
        # Sort by score and select top candidates
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Select ensuring variety (different matches)
        selected = []
        used_matches = set()
        
        for candidate in candidates:
            if candidate["match_id"] not in used_matches:
                selected.append(candidate)
                used_matches.add(candidate["match_id"])
                if len(selected) >= request.num_selections:
                    break
        
        if len(selected) < request.num_selections:
            raise HTTPException(
                status_code=400,
                detail=f"No se pueden generar {request.num_selections} selecciones diferentes"
            )
        
        # Calculate totals
        total_odds = 1.0
        for sel in selected:
            total_odds *= sel["odds"]
        
        avg_confidence = sum(s["confidence"] for s in selected) / len(selected)
        
        # Generate parlay result
        parlay = {
            "id": str(uuid.uuid4()),
            "name": f"Combinada Auto - {request.risk_level.upper()}",
            "selections": selected,
            "total_odds": round(total_odds, 2),
            "stake": request.stake,
            "potential_profit": round(request.stake * total_odds, 2) if request.stake else None,
            "avg_confidence": round(avg_confidence, 1),
            "risk_level": request.risk_level,
            "sports_included": list(set(s["sport"] for s in selected)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "is_auto_generated": True,
            "recommendation": get_parlay_recommendation(total_odds, avg_confidence, request.risk_level)
        }
        
        return parlay
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating auto parlay: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar combinada: {str(e)}")

def get_parlay_recommendation(total_odds: float, confidence: float, risk_level: str) -> dict:
    """Generate recommendation based on parlay analysis"""
    
    # Calculate win probability estimate
    implied_prob = (1 / total_odds) * 100
    
    # Adjust based on confidence
    adjusted_prob = implied_prob * (confidence / 100) * 1.1  # Slight boost for our analysis
    
    # Determine recommendation
    if adjusted_prob > 40:
        rating = "ALTA"
        emoji = "🟢"
        message = "Combinada con buena probabilidad. Considerar apuesta moderada."
    elif adjusted_prob > 25:
        rating = "MEDIA"
        emoji = "🟡"
        message = "Combinada equilibrada. Apostar con precaución."
    else:
        rating = "BAJA"
        emoji = "🔴"
        message = "Combinada arriesgada. Solo para apuestas pequeñas."
    
    # Stake suggestion based on bankroll management
    suggested_stake_pct = {
        "low": 3.0,
        "medium": 2.0,
        "high": 1.0
    }.get(risk_level, 2.0)
    
    return {
        "rating": rating,
        "emoji": emoji,
        "message": message,
        "win_probability": round(adjusted_prob, 1),
        "suggested_stake_percentage": suggested_stake_pct,
        "tip": f"Apuesta sugerida: {suggested_stake_pct}% de tu bankroll"
    }

@api_router.get("/parlays/suggestions")
async def get_parlay_suggestions():
    """Get multiple auto-generated parlay suggestions"""
    suggestions = []
    
    # Generate 3 different parlays with different risk levels
    for risk, num in [("low", 2), ("medium", 3), ("high", 4)]:
        try:
            request = AutoParlayRequest(
                num_selections=num,
                risk_level=risk,
                stake=10000  # Example stake
            )
            parlay = await generate_auto_parlay(request)
            suggestions.append(parlay)
        except Exception as e:
            logger.warning(f"Could not generate {risk} parlay: {e}")
            continue
    
    return {"suggestions": suggestions, "total": len(suggestions)}

# ============== PARLAYS / COMBINADAS ==============

class ParlayResultUpdate(BaseModel):
    result: str  # "won" or "lost"

@api_router.post("/parlays")
async def create_parlay(parlay_data: ParlayCreate, current_user: dict = Depends(get_current_user)):
    if len(parlay_data.selections) > 6:
        raise HTTPException(status_code=400, detail="Máximo 6 selecciones por combinada")
    
    total_odds = 1.0
    for sel in parlay_data.selections:
        total_odds *= sel.get("odds", 1)
    
    parlay = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "name": parlay_data.name,
        "selections": parlay_data.selections,
        "total_odds": round(total_odds, 2),
        "stake": parlay_data.stake,
        "potential_profit": round(parlay_data.stake * total_odds, 2) if parlay_data.stake else None,
        "status": "pending",  # pending, won, lost
        "actual_profit": None,
        "result_date": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Create a copy for returning (insert_one modifies the dict adding _id)
    parlay_response = parlay.copy()
    await db.parlays.insert_one(parlay)
    return parlay_response

@api_router.get("/parlays")
async def get_parlays(skip: int = 0, limit: int = 20, status: str = None, current_user: dict = Depends(get_current_user)):
    query = {"user_id": current_user["id"]}
    if status and status in ["pending", "won", "lost"]:
        query["status"] = status
    
    parlays = await db.parlays.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.parlays.count_documents(query)
    return {"parlays": parlays, "total": total, "skip": skip, "limit": limit}

@api_router.put("/parlays/{parlay_id}/result")
async def update_parlay_result(parlay_id: str, result_data: ParlayResultUpdate, current_user: dict = Depends(get_current_user)):
    """Marcar una combinada como ganada o perdida"""
    if result_data.result not in ["won", "lost"]:
        raise HTTPException(status_code=400, detail="Resultado debe ser 'won' o 'lost'")
    
    # Find the parlay
    parlay = await db.parlays.find_one({"id": parlay_id, "user_id": current_user["id"]}, {"_id": 0})
    if not parlay:
        raise HTTPException(status_code=404, detail="Combinada no encontrada")
    
    # Calculate actual profit
    stake = parlay.get("stake", 0) or 0
    total_odds = parlay.get("total_odds", 1)
    
    if result_data.result == "won":
        actual_profit = round(stake * total_odds - stake, 2)  # Net profit
    else:
        actual_profit = -stake  # Lost the stake
    
    # Update the parlay
    await db.parlays.update_one(
        {"id": parlay_id, "user_id": current_user["id"]},
        {"$set": {
            "status": result_data.result,
            "actual_profit": actual_profit,
            "result_date": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "message": f"Combinada marcada como {'ganada' if result_data.result == 'won' else 'perdida'}",
        "actual_profit": actual_profit
    }

@api_router.get("/parlays/stats")
async def get_parlay_stats(current_user: dict = Depends(get_current_user)):
    """Obtener estadísticas de ROI y rendimiento de combinadas"""
    
    # Get all user parlays
    parlays = await db.parlays.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    
    if not parlays:
        return {
            "total_parlays": 0,
            "pending": 0,
            "won": 0,
            "lost": 0,
            "win_rate": 0,
            "total_staked": 0,
            "total_profit": 0,
            "roi": 0,
            "best_win": None,
            "worst_loss": None,
            "current_streak": {"type": None, "count": 0},
            "avg_odds": 0
        }
    
    # Calculate stats
    total = len(parlays)
    pending = sum(1 for p in parlays if p.get("status") == "pending" or p.get("status") == "active")
    won = sum(1 for p in parlays if p.get("status") == "won")
    lost = sum(1 for p in parlays if p.get("status") == "lost")
    
    completed = won + lost
    win_rate = round((won / completed * 100), 1) if completed > 0 else 0
    
    total_staked = sum(p.get("stake", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    total_profit = sum(p.get("actual_profit", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    
    roi = round((total_profit / total_staked * 100), 1) if total_staked > 0 else 0
    
    # Best win and worst loss
    won_parlays = [p for p in parlays if p.get("status") == "won"]
    lost_parlays = [p for p in parlays if p.get("status") == "lost"]
    
    best_win = None
    if won_parlays:
        best = max(won_parlays, key=lambda x: x.get("actual_profit", 0) or 0)
        best_win = {
            "name": best.get("name"),
            "profit": best.get("actual_profit"),
            "odds": best.get("total_odds"),
            "date": best.get("result_date")
        }
    
    worst_loss = None
    if lost_parlays:
        worst = min(lost_parlays, key=lambda x: x.get("actual_profit", 0) or 0)
        worst_loss = {
            "name": worst.get("name"),
            "loss": abs(worst.get("actual_profit", 0) or 0),
            "odds": worst.get("total_odds"),
            "date": worst.get("result_date")
        }
    
    # Current streak
    completed_parlays = sorted(
        [p for p in parlays if p.get("status") in ["won", "lost"] and p.get("result_date")],
        key=lambda x: x.get("result_date", ""),
        reverse=True
    )
    
    streak_type = None
    streak_count = 0
    if completed_parlays:
        streak_type = completed_parlays[0].get("status")
        for p in completed_parlays:
            if p.get("status") == streak_type:
                streak_count += 1
            else:
                break
    
    # Average odds
    all_odds = [p.get("total_odds", 0) for p in parlays if p.get("total_odds")]
    avg_odds = round(sum(all_odds) / len(all_odds), 2) if all_odds else 0
    
    # Monthly breakdown
    monthly_stats = {}
    for p in parlays:
        if p.get("status") in ["won", "lost"] and p.get("result_date"):
            month_key = p["result_date"][:7]  # YYYY-MM
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {"won": 0, "lost": 0, "profit": 0, "staked": 0}
            
            monthly_stats[month_key][p["status"]] += 1
            monthly_stats[month_key]["profit"] += p.get("actual_profit", 0) or 0
            monthly_stats[month_key]["staked"] += p.get("stake", 0) or 0
    
    return {
        "total_parlays": total,
        "pending": pending,
        "won": won,
        "lost": lost,
        "win_rate": win_rate,
        "total_staked": round(total_staked, 2),
        "total_profit": round(total_profit, 2),
        "roi": roi,
        "best_win": best_win,
        "worst_loss": worst_loss,
        "current_streak": {"type": streak_type, "count": streak_count},
        "avg_odds": avg_odds,
        "monthly_stats": monthly_stats
    }

@api_router.delete("/parlays/{parlay_id}")
async def delete_parlay(parlay_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.parlays.delete_one({"id": parlay_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Parlay not found")
    return {"message": "Parlay eliminado"}

# ============== AI ANALYSIS ==============

@api_router.post("/ai/analyze")
async def analyze_match(request: AIAnalysisRequest, current_user: dict = Depends(get_current_user)):
    match = generate_mock_matches(count=1)[0]
    match["id"] = request.match_id
    
    # Generate analysis based on stats (without external AI for free deployment)
    home_form = match['stats']['home']['form']
    away_form = match['stats']['away']['form']
    home_wins = home_form.count('W')
    away_wins = away_form.count('W')
    
    home_strength = (match['stats']['home']['possession'] / 100) * 0.3 + (match['stats']['home']['xG'] / 3) * 0.4 + (home_wins / 5) * 0.3
    away_strength = (match['stats']['away']['possession'] / 100) * 0.3 + (match['stats']['away']['xG'] / 3) * 0.4 + (away_wins / 5) * 0.3
    
    total_strength = home_strength + away_strength + 0.2  # 0.2 for draw probability
    home_prob = round((home_strength / total_strength) * 100, 1)
    away_prob = round((away_strength / total_strength) * 100, 1)
    draw_prob = round(100 - home_prob - away_prob, 1)
    
    # Check for value bets
    home_implied = round((1 / match['odds']['Bet365']['home']) * 100, 1)
    away_implied = round((1 / match['odds']['Bet365']['away']) * 100, 1)
    
    value_bet = None
    if home_prob > home_implied + 5:
        value_bet = f"✅ VALUE BET en {match['home_team']} (Local) - Prob. real {home_prob}% vs implícita {home_implied}%"
    elif away_prob > away_implied + 5:
        value_bet = f"✅ VALUE BET en {match['away_team']} (Visitante) - Prob. real {away_prob}% vs implícita {away_implied}%"
    else:
        value_bet = "❌ No se detecta value bet claro en este partido"
    
    analysis = f"""📊 **Análisis de {match['home_team']} vs {match['away_team']}**

**Estadísticas del Local ({match['home_team']}):**
- Posesión: {match['stats']['home']['possession']}%
- Expected Goals (xG): {match['stats']['home']['xG']}
- Forma reciente: {' '.join(match['stats']['home']['form'])}

**Estadísticas del Visitante ({match['away_team']}):**
- Posesión: {match['stats']['away']['possession']}%
- Expected Goals (xG): {match['stats']['away']['xG']}
- Forma reciente: {' '.join(match['stats']['away']['form'])}

**Probabilidades Calculadas:**
- {match['home_team']} (Local): {home_prob}%
- Empate: {draw_prob}%
- {match['away_team']} (Visitante): {away_prob}%

**Cuotas disponibles:**
- Local: {match['odds']['Bet365']['home']}
- Empate: {match['odds']['Bet365']['draw']}
- Visitante: {match['odds']['Bet365']['away']}

**Recomendación:**
{value_bet}

**Nota:** Este análisis utiliza algoritmos estadísticos basados en xG, posesión y forma reciente."""
    
    return {
        "match_id": request.match_id,
        "match": match,
        "analysis": analysis,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

# ============== HISTORY & STATS ==============

@api_router.post("/predictions")
async def save_prediction(prediction: PredictionCreate, current_user: dict = Depends(get_current_user)):
    pred_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "match_id": prediction.match_id,
        "prediction_type": prediction.prediction_type,
        "selection": prediction.selection,
        "odds": prediction.odds,
        "stake": prediction.stake,
        "result": "pending",
        "profit": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    # Create a copy for returning (insert_one modifies the dict adding _id)
    pred_response = pred_doc.copy()
    await db.predictions.insert_one(pred_doc)
    return pred_response

@api_router.get("/predictions")
async def get_predictions(skip: int = 0, limit: int = 50, current_user: dict = Depends(get_current_user)):
    predictions = await db.predictions.find({"user_id": current_user["id"]}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.predictions.count_documents({"user_id": current_user["id"]})
    return {"predictions": predictions, "total": total, "skip": skip, "limit": limit}

@api_router.get("/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    # Use aggregation for efficient stats calculation
    pipeline = [
        {"$match": {"user_id": current_user["id"]}},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "won": {"$sum": {"$cond": [{"$eq": ["$result", "won"]}, 1, 0]}},
            "lost": {"$sum": {"$cond": [{"$eq": ["$result", "lost"]}, 1, 0]}},
            "pending": {"$sum": {"$cond": [{"$eq": ["$result", "pending"]}, 1, 0]}},
            "total_stake": {"$sum": {"$ifNull": ["$stake", 0]}},
            "total_profit": {"$sum": {"$ifNull": ["$profit", 0]}}
        }}
    ]
    result = await db.predictions.aggregate(pipeline).to_list(1)
    
    if result:
        stats = result[0]
        total = stats["total"]
        won = stats["won"]
        lost = stats["lost"]
        pending = stats["pending"]
        total_stake = stats["total_stake"]
        total_profit = stats["total_profit"]
    else:
        total = won = lost = pending = 0
        total_stake = total_profit = 0
    
    return {
        "total_predictions": total,
        "won": won,
        "lost": lost,
        "pending": pending,
        "win_rate": round((won / (won + lost)) * 100, 1) if (won + lost) > 0 else 0,
        "total_stake": total_stake,
        "total_profit": total_profit,
        "roi": round((total_profit / total_stake) * 100, 1) if total_stake > 0 else 0
    }

# ============== SPORTS & LEAGUES ==============

@api_router.get("/sports")
async def get_sports():
    return {
        "sports": [
            {"id": "football", "name": "Fútbol", "icon": "soccer-ball"},
            {"id": "basketball", "name": "Baloncesto", "icon": "basketball"},
            {"id": "tennis", "name": "Tenis", "icon": "tennis-ball"},
            {"id": "baseball", "name": "Béisbol", "icon": "baseball"},
            {"id": "hockey", "name": "Hockey", "icon": "hockey"},
            {"id": "mma", "name": "MMA / UFC", "icon": "hand-fist"},
            {"id": "esports", "name": "Esports", "icon": "game-controller"}
        ]
    }

@api_router.get("/leagues/{sport}")
async def get_leagues(sport: str):
    leagues = LEAGUES.get(sport, [])
    return {"sport": sport, "leagues": leagues}

# ============== HEALTH CHECK ==============

@api_router.get("/")
async def root():
    return {"message": "SportsBetAI API v1.0", "status": "online"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@api_router.get("/health/db")
async def db_health_check():
    """Verificar conexión a MongoDB"""
    try:
        # Intentar hacer un ping a la base de datos
        await db.command("ping")
        user_count = await db.users.count_documents({})
        return {
            "status": "connected",
            "database": os.environ.get('DB_NAME', 'unknown'),
            "users_count": user_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"DB Health check failed: {str(e)}")
        return {
            "status": "disconnected",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
