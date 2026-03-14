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
from emergentintegrations.llm.chat import LlmChat, UserMessage

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
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
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

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"])
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        telegram_chat_id=user.get("telegram_chat_id"),
        created_at=user["created_at"]
    )
    return TokenResponse(access_token=token, user=user_response)

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
    matches = generate_mock_matches(sport, limit)
    if status:
        matches = [m for m in matches if m["status"] == status]
    return {"matches": matches, "total": len(matches)}

@api_router.get("/matches/{match_id}")
async def get_match(match_id: str):
    # In real app, fetch from DB. Here we generate a mock
    matches = generate_mock_matches()
    for m in matches:
        if m["id"] == match_id:
            return m
    # Generate a random one for demo
    match = generate_mock_matches(count=1)[0]
    match["id"] = match_id
    return match

@api_router.get("/matches/live")
async def get_live_matches():
    matches = generate_mock_matches(count=30)
    live = [m for m in matches if m["status"] == "live"]
    return {"matches": live, "total": len(live)}

# ============== VALUE BETS ENDPOINTS ==============

@api_router.get("/value-bets")
async def get_value_bets(sport: str = None, min_value: float = 3.0):
    matches = generate_mock_matches(sport, count=30)
    value_bets = calculate_value_bets(matches)
    filtered = [vb for vb in value_bets if vb["value_percentage"] >= min_value]
    return {"value_bets": filtered, "total": len(filtered)}

@api_router.get("/value-bets/top")
async def get_top_value_bets(limit: int = 5):
    matches = generate_mock_matches(count=50)
    value_bets = calculate_value_bets(matches)
    return {"value_bets": value_bets[:limit]}

# ============== ODDS COMPARISON ==============

@api_router.get("/odds/compare/{match_id}")
async def compare_odds(match_id: str):
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
        }
    }
    
    for market in ["home", "draw", "away"]:
        best_odds = 0
        best_bookmaker = ""
        for bookmaker, odds in match["odds"].items():
            if odds[market] > best_odds:
                best_odds = odds[market]
                best_bookmaker = bookmaker
        comparison["best_odds"][market] = {"bookmaker": best_bookmaker, "odds": best_odds}
    
    return comparison

# ============== PARLAYS / COMBINADAS ==============

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
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Create a copy for returning (insert_one modifies the dict adding _id)
    parlay_response = parlay.copy()
    await db.parlays.insert_one(parlay)
    return parlay_response

@api_router.get("/parlays")
async def get_parlays(current_user: dict = Depends(get_current_user)):
    parlays = await db.parlays.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(100)
    return {"parlays": parlays}

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
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"analysis_{request.match_id}_{current_user['id']}",
            system_message="""Eres un experto analista de apuestas deportivas. Analiza partidos considerando:
            - Estadísticas históricas y forma reciente
            - Cuotas y valor esperado
            - Factores externos (lesiones, motivación, etc.)
            Proporciona análisis concisos y recomendaciones claras en español."""
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""Analiza este partido:
        
        {match['home_team']} vs {match['away_team']}
        Liga: {match['league']}
        Deporte: {match['sport']}
        
        Estadísticas:
        - {match['home_team']}: Posesión {match['stats']['home']['possession']}%, xG {match['stats']['home']['xG']}, Forma: {' '.join(match['stats']['home']['form'])}
        - {match['away_team']}: Posesión {match['stats']['away']['possession']}%, xG {match['stats']['away']['xG']}, Forma: {' '.join(match['stats']['away']['form'])}
        
        Cuotas promedio:
        - Local: {match['odds']['Bet365']['home']}
        - Empate: {match['odds']['Bet365']['draw']}
        - Visitante: {match['odds']['Bet365']['away']}
        
        Proporciona:
        1. Análisis breve del partido
        2. Probabilidades estimadas para cada resultado
        3. ¿Hay value bet? ¿En qué selección?
        4. Recomendación de apuesta (si existe valor)"""
        
        user_message = UserMessage(text=prompt)
        analysis = await chat.send_message(user_message)
        
        return {
            "match_id": request.match_id,
            "match": match,
            "analysis": analysis,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"AI Analysis error: {e}")
        # Fallback analysis
        return {
            "match_id": request.match_id,
            "match": match,
            "analysis": f"""📊 **Análisis de {match['home_team']} vs {match['away_team']}**

El equipo local muestra una posesión del {match['stats']['home']['possession']}% con un xG de {match['stats']['home']['xG']}. 
Forma reciente: {' '.join(match['stats']['home']['form'])}

El visitante tiene {match['stats']['away']['possession']}% de posesión y xG de {match['stats']['away']['xG']}.
Forma reciente: {' '.join(match['stats']['away']['form'])}

**Recomendación:** Basado en las estadísticas, el mercado de Over/Under 2.5 goles podría ofrecer valor.""",
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
async def get_predictions(current_user: dict = Depends(get_current_user)):
    predictions = await db.predictions.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(100)
    return {"predictions": predictions}

@api_router.get("/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    predictions = await db.predictions.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    
    total = len(predictions)
    won = len([p for p in predictions if p.get("result") == "won"])
    lost = len([p for p in predictions if p.get("result") == "lost"])
    pending = len([p for p in predictions if p.get("result") == "pending"])
    
    total_stake = sum(p.get("stake", 0) for p in predictions)
    total_profit = sum(p.get("profit", 0) or 0 for p in predictions)
    
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
