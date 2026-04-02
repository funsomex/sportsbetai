"""
Matches and sports data routes
"""
from fastapi import APIRouter, Query
from typing import Optional, List

from services.odds_service import get_all_real_matches, get_cache_stats
from services.mock_service import generate_mock_matches
from services.valuebets_service import calculate_real_value_bets, calculate_mock_value_bets
from config.settings import THE_ODDS_API_KEY

import logging
import urllib.parse
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Matches"])


@router.get("/matches")
async def get_matches(
    sport: Optional[str] = None,
    league: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    date_filter: Optional[str] = None
):
    """Get matches with real data (cached) or fallback to demo"""
    source = "demo"
    matches = []
    
    if THE_ODDS_API_KEY:
        try:
            real_matches = await get_all_real_matches()
            if real_matches and len(real_matches) > 0:
                matches = real_matches
                source = "real"
        except Exception as e:
            logger.error(f"Error fetching real matches: {e}")
    
    # Fallback to mock data
    if not matches:
        matches = generate_mock_matches(count=limit, sport_filter=sport, date_filter=date_filter)
        source = "demo"
    
    # Apply filters
    if sport:
        matches = [m for m in matches if m.get("sport") == sport or sport in m.get("league", "").lower()]
    if league:
        matches = [m for m in matches if league.lower() in m.get("league", "").lower()]
    if status:
        matches = [m for m in matches if m.get("status") == status]
    
    return {
        "matches": matches[:limit],
        "total": len(matches),
        "source": source
    }


@router.get("/matches/cache-stats")
async def get_matches_cache_stats():
    """Get cache statistics for debugging"""
    return get_cache_stats()


@router.get("/value-bets")
async def get_value_bets(sport: str = None, min_value: float = 2.0):
    """Get value bets - uses real odds data if available"""
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches()
            if matches and len(matches) > 0:
                value_bets = calculate_real_value_bets(matches)
                filtered = [vb for vb in value_bets if vb["value_percentage"] >= min_value]
                return {"value_bets": filtered, "total": len(filtered), "source": "real"}
        except Exception as e:
            logger.error(f"Error calculating real value bets: {e}")
    
    # Fallback to mock
    matches = generate_mock_matches(count=50)
    value_bets = calculate_mock_value_bets(matches)
    filtered = [vb for vb in value_bets if vb["value_percentage"] >= min_value]
    return {"value_bets": filtered, "total": len(filtered), "source": "demo", "message": "Demo data"}


@router.get("/value-bets/top")
async def get_top_value_bets(limit: int = 5):
    """Get top value bets"""
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches()
            if matches and len(matches) > 0:
                value_bets = calculate_real_value_bets(matches)
                return {"value_bets": value_bets[:limit], "source": "real"}
        except Exception as e:
            logger.error(f"Error getting top value bets: {e}")
    
    # Fallback to mock
    matches = generate_mock_matches(count=50)
    value_bets = calculate_mock_value_bets(matches)
    return {"value_bets": value_bets[:limit], "source": "demo"}


@router.get("/bet-of-the-day")
async def get_bet_of_the_day():
    """Get the best value bet of the day - single top pick with sharing info"""
    best_bet = None
    source = "demo"
    
    if THE_ODDS_API_KEY:
        try:
            matches = await get_all_real_matches()
            if matches and len(matches) > 0:
                value_bets = calculate_real_value_bets(matches)
                if value_bets:
                    # Score = value_percentage * 0.6 + confidence * 0.4
                    scored_bets = []
                    for vb in value_bets:
                        score = (vb["value_percentage"] * 0.6) + (vb["confidence"] * 0.4)
                        scored_bets.append((score, vb))
                    scored_bets.sort(key=lambda x: x[0], reverse=True)
                    best_bet = scored_bets[0][1]
                    source = "real"
        except Exception as e:
            logger.error(f"Error getting bet of the day: {e}")
    
    # Fallback to mock
    if not best_bet:
        matches = generate_mock_matches(count=50)
        value_bets = calculate_mock_value_bets(matches)
        if value_bets:
            scored_bets = []
            for vb in value_bets:
                score = (vb["value_percentage"] * 0.6) + (vb["confidence"] * 0.4)
                scored_bets.append((score, vb))
            scored_bets.sort(key=lambda x: x[0], reverse=True)
            best_bet = scored_bets[0][1]
    
    if not best_bet:
        return {"bet": None, "message": "No bets available today"}
    
    # Generate shareable text
    share_text = f"🎯 APUESTA DEL DÍA - SportsBetAI\n\n⚽ {best_bet['match']['home_team']} vs {best_bet['match']['away_team']}\n🏆 {best_bet['match']['league']}\n\n📊 {best_bet['selection']} @ {best_bet['odds']}\n📈 Valor: +{best_bet['value_percentage']}%\n🎯 Confianza: {best_bet['confidence']}%\n🏠 Casa: {best_bet['bookmaker']}"
    
    encoded_text = urllib.parse.quote(share_text)
    
    return {
        "bet": best_bet,
        "source": source,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "share": {
            "text": share_text,
            "twitter_url": f"https://twitter.com/intent/tweet?text={encoded_text}",
            "whatsapp_url": f"https://wa.me/?text={encoded_text}",
            "telegram_url": f"https://t.me/share/url?text={encoded_text}"
        }
    }


@router.get("/odds/compare/{match_id}")
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
        if best_odds > 0:
            comparison["best_odds"][market] = {"bookmaker": best_bookmaker, "odds": best_odds}
    
    return comparison
