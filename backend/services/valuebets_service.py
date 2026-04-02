"""
Value Bets calculation service
"""
import random
import uuid
from datetime import datetime, timezone
from typing import List, Dict


def calculate_real_value_bets(matches: List[Dict]) -> List[Dict]:
    """Calculate value bets from real odds data"""
    value_bets = []
    
    for match in matches:
        if not match.get("odds"):
            continue
        
        # Calculate average odds and find discrepancies
        all_home_odds = []
        all_draw_odds = []
        all_away_odds = []
        
        for bookmaker, odds in match["odds"].items():
            if "home" in odds:
                all_home_odds.append((bookmaker, odds["home"]))
            if "draw" in odds:
                all_draw_odds.append((bookmaker, odds["draw"]))
            if "away" in odds:
                all_away_odds.append((bookmaker, odds["away"]))
        
        # Analyze each market
        for market_name, odds_list in [("home", all_home_odds), ("draw", all_draw_odds), ("away", all_away_odds)]:
            if len(odds_list) < 3:
                continue
            
            odds_values = [o[1] for o in odds_list]
            avg_odds = sum(odds_values) / len(odds_values)
            max_odds_entry = max(odds_list, key=lambda x: x[1])
            
            # Calculate value percentage
            implied_prob = 1 / avg_odds
            best_implied = 1 / max_odds_entry[1]
            value_pct = ((implied_prob / best_implied) - 1) * 100
            
            if value_pct > 3:  # Value bet threshold
                selection_name = match["home_team"] if market_name == "home" else (
                    "Empate" if market_name == "draw" else match["away_team"]
                )
                
                value_bet = {
                    "id": str(uuid.uuid4()),
                    "match_id": match["id"],
                    "match": {
                        "id": match["id"],
                        "home_team": match["home_team"],
                        "away_team": match["away_team"],
                        "league": match["league"],
                        "sport": match["sport"],
                        "start_time": match["start_time"]
                    },
                    "market": market_name,
                    "selection": selection_name,
                    "bookmaker": max_odds_entry[0],
                    "odds": round(max_odds_entry[1], 2),
                    "true_probability": round(implied_prob * 100, 1),
                    "implied_probability": round(best_implied * 100, 1),
                    "value_percentage": round(value_pct, 1),
                    "confidence": min(85, 40 + int(value_pct * 2)),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                value_bets.append(value_bet)
    
    # Sort by value percentage
    value_bets.sort(key=lambda x: x["value_percentage"], reverse=True)
    return value_bets[:20]


def calculate_mock_value_bets(matches: List[Dict]) -> List[Dict]:
    """Calculate value bets from mock data"""
    value_bets = []
    
    for match in matches:
        if not match.get("odds"):
            continue
        
        for market in ["home", "draw", "away"]:
            if random.random() > 0.3:  # 30% chance to create value bet
                continue
            
            best_odds = 0
            best_bookmaker = ""
            
            for bookmaker, odds in match["odds"].items():
                if market in odds and odds[market] > best_odds:
                    best_odds = odds[market]
                    best_bookmaker = bookmaker
            
            if best_odds > 0:
                value_percentage = random.uniform(3, 15)
                
                if value_percentage > 3:
                    selection = match["home_team"] if market == "home" else (
                        "Empate" if market == "draw" else match["away_team"]
                    )
                    
                    value_bet = {
                        "id": str(uuid.uuid4()),
                        "match_id": match["id"],
                        "match": {
                            "id": match["id"],
                            "home_team": match["home_team"],
                            "away_team": match["away_team"],
                            "league": match["league"],
                            "sport": match.get("sport", "football"),
                            "start_time": match["start_time"]
                        },
                        "market": market,
                        "selection": selection,
                        "bookmaker": best_bookmaker,
                        "odds": round(best_odds, 2),
                        "true_probability": round(random.uniform(30, 70), 1),
                        "implied_probability": round(1 / best_odds * 100, 1),
                        "value_percentage": round(value_percentage, 1),
                        "confidence": min(85, random.randint(45, 80)),
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    value_bets.append(value_bet)
    
    value_bets.sort(key=lambda x: x["value_percentage"], reverse=True)
    return value_bets[:15]
