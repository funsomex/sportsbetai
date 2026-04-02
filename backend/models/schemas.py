"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any


# ============== AUTH MODELS ==============

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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str


# ============== MATCH MODELS ==============

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
    is_real_data: Optional[bool] = False


# ============== VALUE BET MODELS ==============

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


# ============== PARLAY MODELS ==============

class Parlay(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    name: str
    selections: List[Dict[str, Any]]
    total_odds: float
    stake: Optional[float] = None
    potential_profit: Optional[float] = None
    status: str  # "pending", "won", "lost"
    created_at: str


class ParlayCreate(BaseModel):
    selections: List[Dict[str, Any]]
    name: str = "Mi Combinada"
    stake: Optional[float] = None


class ParlayGenerateRequest(BaseModel):
    num_selections: int = Field(default=3, ge=2, le=6)
    risk_level: str = Field(default="medium")  # low, medium, high
    sports: Optional[List[str]] = None
    date_filter: Optional[str] = None  # today, tomorrow, week, specific date
    specific_date: Optional[str] = None  # YYYY-MM-DD format


class ParlayStatusUpdate(BaseModel):
    status: str  # "won" or "lost"


# ============== PREDICTION MODELS ==============

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


class PredictionCreate(BaseModel):
    match_id: str
    prediction_type: str
    selection: str
    odds: float
    stake: float = 0


# ============== AI/ANALYSIS MODELS ==============

class AIAnalysisRequest(BaseModel):
    match_id: str
    analysis_type: str = "general"
