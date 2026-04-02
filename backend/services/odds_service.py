"""
The Odds API service for fetching real sports data
"""
import httpx
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from config.settings import (
    THE_ODDS_API_KEY, 
    THE_ODDS_API_BASE, 
    ODDS_API_SPORTS, 
    SPORT_DISPLAY_NAMES,
    CACHE_TTL_MINUTES
)

logger = logging.getLogger(__name__)

# In-memory cache for API responses
_matches_cache = {
    "data": None,
    "timestamp": None
}


def is_cache_valid() -> bool:
    """Check if cache is still valid (within TTL)"""
    if _matches_cache["data"] is None or _matches_cache["timestamp"] is None:
        return False
    cache_age = datetime.now(timezone.utc) - _matches_cache["timestamp"]
    return cache_age.total_seconds() < (CACHE_TTL_MINUTES * 60)


def get_cached_matches() -> Optional[List[Dict]]:
    """Get matches from cache if valid"""
    if is_cache_valid():
        logger.info(f"Using cached matches data (age: {(datetime.now(timezone.utc) - _matches_cache['timestamp']).total_seconds():.0f}s)")
        return _matches_cache["data"]
    return None


def update_cache(matches: List[Dict]):
    """Update the cache with new matches data"""
    _matches_cache["data"] = matches
    _matches_cache["timestamp"] = datetime.now(timezone.utc)
    logger.info(f"Cache updated with {len(matches)} matches")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    if _matches_cache["timestamp"]:
        cache_age = (datetime.now(timezone.utc) - _matches_cache["timestamp"]).total_seconds()
        return {
            "cache_valid": is_cache_valid(),
            "cache_age_seconds": cache_age,
            "cache_ttl_minutes": CACHE_TTL_MINUTES,
            "cached_matches_count": len(_matches_cache["data"]) if _matches_cache["data"] else 0,
            "next_refresh_in_seconds": max(0, (CACHE_TTL_MINUTES * 60) - cache_age)
        }
    return {
        "cache_valid": False,
        "cache_age_seconds": None,
        "cache_ttl_minutes": CACHE_TTL_MINUTES,
        "cached_matches_count": 0,
        "next_refresh_in_seconds": 0
    }


async def fetch_real_matches_from_api(sport_key: str) -> List[Dict]:
    """Fetch matches from The Odds API"""
    if not THE_ODDS_API_KEY:
        return []
    
    url = f"{THE_ODDS_API_BASE}/sports/{sport_key}/odds"
    params = {
        "apiKey": THE_ODDS_API_KEY,
        "regions": "us,eu,uk",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=15.0)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error("The Odds API: Invalid API key")
            elif response.status_code == 429:
                logger.warning("The Odds API: Rate limit exceeded")
            else:
                logger.error(f"The Odds API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching from The Odds API: {e}")
    return []


def transform_odds_api_match(match: Dict, sport_key: str) -> Dict:
    """Transform The Odds API response to our match format"""
    odds_by_bookmaker = {}
    
    for bookmaker in match.get("bookmakers", []):
        bookmaker_name = bookmaker.get("title", "Unknown")
        bookmaker_odds = {}
        
        for market in bookmaker.get("markets", []):
            if market["key"] == "h2h":
                for outcome in market.get("outcomes", []):
                    if outcome["name"] == match.get("home_team"):
                        bookmaker_odds["home"] = outcome["price"]
                    elif outcome["name"] == match.get("away_team"):
                        bookmaker_odds["away"] = outcome["price"]
                    elif outcome["name"] == "Draw":
                        bookmaker_odds["draw"] = outcome["price"]
        
        if bookmaker_odds:
            odds_by_bookmaker[bookmaker_name] = bookmaker_odds
    
    league_name = SPORT_DISPLAY_NAMES.get(sport_key, sport_key)
    
    # Determine sport category
    sport_category = "other"
    if "soccer" in sport_key:
        sport_category = "football"
    elif "basketball" in sport_key:
        sport_category = "basketball"
    elif "baseball" in sport_key:
        sport_category = "baseball"
    elif "hockey" in sport_key or "icehockey" in sport_key:
        sport_category = "hockey"
    elif "mma" in sport_key:
        sport_category = "mma"
    elif "tennis" in sport_key:
        sport_category = "tennis"
    elif "esports" in sport_key:
        sport_category = "esports"
    
    return {
        "id": match.get("id"),
        "sport": sport_category,
        "league": league_name,
        "home_team": match.get("home_team"),
        "away_team": match.get("away_team"),
        "start_time": match.get("commence_time"),
        "status": "upcoming",
        "home_score": None,
        "away_score": None,
        "odds": odds_by_bookmaker,
        "stats": None,
        "is_real_data": True
    }


async def get_all_real_matches() -> Optional[List[Dict]]:
    """Get all real matches, using cache if available"""
    # Check cache first
    cached = get_cached_matches()
    if cached is not None:
        return cached
    
    # No valid cache, fetch from API
    if not THE_ODDS_API_KEY:
        return None
    
    all_matches = []
    sports_to_fetch = ["soccer_epl", "soccer_spain_la_liga", "basketball_nba", 
                       "baseball_mlb", "icehockey_nhl", "mma_mixed_martial_arts"]
    
    for sport_key in sports_to_fetch:
        try:
            matches = await fetch_real_matches_from_api(sport_key)
            for match in matches:
                transformed = transform_odds_api_match(match, sport_key)
                if transformed.get("odds"):
                    all_matches.append(transformed)
        except Exception as e:
            logger.error(f"Error fetching {sport_key}: {e}")
    
    # Update cache if we got data
    if all_matches:
        update_cache(all_matches)
    
    return all_matches if all_matches else None
