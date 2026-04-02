"""
Parlays (Combinadas) routes
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query

from models.schemas import ParlayCreate, ParlayGenerateRequest, ParlayStatusUpdate
from services.auth_service import get_current_user
from services.odds_service import get_all_real_matches
from services.mock_service import generate_mock_matches
from services.ai_service import generate_parlay_with_ai
from config.database import db
from config.settings import THE_ODDS_API_KEY

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/parlays", tags=["Parlays"])


@router.get("/stats")
async def get_parlay_stats(current_user: dict = Depends(get_current_user)):
    """Get parlay statistics for the current user"""
    parlays = await db.parlays.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    won = sum(1 for p in parlays if p.get("status") == "won")
    lost = sum(1 for p in parlays if p.get("status") == "lost")
    pending = sum(1 for p in parlays if p.get("status") in ["pending", "active"])
    
    total_staked = sum(p.get("stake", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    total_profit = sum(p.get("actual_profit", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    
    win_rate = round((won / (won + lost) * 100), 1) if (won + lost) > 0 else 0
    roi = round((total_profit / total_staked * 100), 1) if total_staked > 0 else 0
    
    # Calculate current streak
    current_streak = {"count": 0, "type": None}
    resolved = [p for p in parlays if p.get("status") in ["won", "lost"]]
    
    if resolved:
        streak_type = resolved[0].get("status")
        streak_count = 0
        for p in resolved:
            if p.get("status") == streak_type:
                streak_count += 1
            else:
                break
        current_streak = {"count": streak_count, "type": streak_type}
    
    return {
        "total_parlays": len(parlays),
        "won": won,
        "lost": lost,
        "pending": pending,
        "win_rate": win_rate,
        "roi": roi,
        "total_staked": round(total_staked, 2),
        "total_profit": round(total_profit, 2),
        "current_streak": current_streak
    }


@router.get("")
async def get_parlays(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's parlays"""
    query = {"user_id": current_user["id"]}
    if status:
        query["status"] = status
    
    parlays = await db.parlays.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"parlays": parlays, "total": len(parlays)}


@router.post("")
async def create_parlay(
    parlay: ParlayCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new parlay"""
    total_odds = 1.0
    for sel in parlay.selections:
        total_odds *= sel.get("odds", 1.0)
    
    potential_profit = None
    if parlay.stake and parlay.stake > 0:
        potential_profit = round((parlay.stake * total_odds) - parlay.stake, 2)
    
    parlay_data = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "name": parlay.name,
        "selections": parlay.selections,
        "total_odds": round(total_odds, 2),
        "stake": parlay.stake,
        "potential_profit": potential_profit,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.parlays.insert_one(parlay_data)
    parlay_data.pop("_id", None)
    
    return parlay_data


@router.post("/generate")
async def generate_parlay(
    request: ParlayGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a parlay using AI analysis"""
    matches = []
    source = "demo"
    
    # Get matches
    if THE_ODDS_API_KEY:
        try:
            real_matches = await get_all_real_matches()
            if real_matches and len(real_matches) > 0:
                matches = real_matches
                source = "real"
        except Exception as e:
            logger.error(f"Error fetching real matches for parlay: {e}")
    
    if not matches:
        matches = generate_mock_matches(count=50, date_filter=request.date_filter)
    
    # Filter by date if specified
    if request.date_filter and matches:
        now = datetime.now(timezone.utc)
        filtered_matches = []
        
        for m in matches:
            try:
                match_time_str = m.get("start_time", "")
                if match_time_str:
                    match_time = datetime.fromisoformat(match_time_str.replace('Z', '+00:00'))
                    
                    if request.date_filter == "today":
                        if match_time.date() == now.date():
                            filtered_matches.append(m)
                    elif request.date_filter == "tomorrow":
                        tomorrow = (now + timedelta(days=1)).date()
                        if match_time.date() == tomorrow:
                            filtered_matches.append(m)
                    elif request.date_filter == "week":
                        week_end = now + timedelta(days=7)
                        if now <= match_time <= week_end:
                            filtered_matches.append(m)
                    elif request.specific_date:
                        specific = datetime.strptime(request.specific_date, "%Y-%m-%d").date()
                        if match_time.date() == specific:
                            filtered_matches.append(m)
                    else:
                        filtered_matches.append(m)
            except Exception:
                filtered_matches.append(m)
        
        if filtered_matches:
            matches = filtered_matches
    
    # Filter by sports
    if request.sports:
        matches = [m for m in matches if m.get("sport") in request.sports]
    
    if len(matches) < request.num_selections:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough matches available. Found {len(matches)}, need {request.num_selections}"
        )
    
    # Generate with AI
    result = await generate_parlay_with_ai(
        matches=matches,
        num_selections=request.num_selections,
        risk_level=request.risk_level,
        sports_filter=request.sports
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Could not generate parlay")
    
    return {
        "parlay": result,
        "source": source,
        "matches_analyzed": len(matches)
    }


@router.patch("/{parlay_id}/status")
async def update_parlay_status(
    parlay_id: str,
    update: ParlayStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update parlay status (won/lost)"""
    if update.status not in ["won", "lost"]:
        raise HTTPException(status_code=400, detail="Status must be 'won' or 'lost'")
    
    parlay = await db.parlays.find_one({
        "id": parlay_id,
        "user_id": current_user["id"]
    })
    
    if not parlay:
        raise HTTPException(status_code=404, detail="Parlay not found")
    
    # Calculate profit/loss
    profit = 0
    if parlay.get("stake"):
        if update.status == "won":
            profit = round((parlay["stake"] * parlay["total_odds"]) - parlay["stake"], 2)
        else:
            profit = -parlay["stake"]
    
    await db.parlays.update_one(
        {"id": parlay_id},
        {
            "$set": {
                "status": update.status,
                "actual_profit": profit,
                "resolved_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "status": "success",
        "parlay_id": parlay_id,
        "new_status": update.status,
        "profit": profit
    }


@router.put("/{parlay_id}/result")
async def update_parlay_result(
    parlay_id: str,
    result_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update parlay result (won/lost) - alternative endpoint for frontend compatibility"""
    result = result_data.get("result")
    if result not in ["won", "lost"]:
        raise HTTPException(status_code=400, detail="Result must be 'won' or 'lost'")
    
    parlay = await db.parlays.find_one({
        "id": parlay_id,
        "user_id": current_user["id"]
    })
    
    if not parlay:
        raise HTTPException(status_code=404, detail="Parlay not found")
    
    # Calculate profit/loss
    profit = 0
    if parlay.get("stake"):
        if result == "won":
            profit = round((parlay["stake"] * parlay["total_odds"]) - parlay["stake"], 2)
        else:
            profit = -parlay["stake"]
    
    await db.parlays.update_one(
        {"id": parlay_id},
        {
            "$set": {
                "status": result,
                "actual_profit": profit,
                "resolved_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "status": "success",
        "parlay_id": parlay_id,
        "new_status": result,
        "profit": profit
    }


@router.delete("/{parlay_id}")
async def delete_parlay(
    parlay_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a parlay"""
    result = await db.parlays.delete_one({
        "id": parlay_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Parlay not found")
    
    return {"status": "success", "message": "Parlay deleted"}


# Import timedelta for date filtering
from datetime import timedelta
