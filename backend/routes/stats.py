"""
Statistics and user metrics routes
"""
from fastapi import APIRouter, Depends
from services.auth_service import get_current_user
from config.database import db

router = APIRouter(tags=["Statistics"])


@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Get user statistics from parlays"""
    parlays = await db.parlays.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(1000)
    
    won = sum(1 for p in parlays if p.get("status") == "won")
    lost = sum(1 for p in parlays if p.get("status") == "lost")
    pending = sum(1 for p in parlays if p.get("status") == "pending")
    total = len(parlays)
    
    total_stake = sum(p.get("stake", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    total_profit = sum(p.get("actual_profit", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    
    win_rate = round((won / (won + lost) * 100), 1) if (won + lost) > 0 else 0
    roi = round((total_profit / total_stake * 100), 1) if total_stake > 0 else 0
    
    return {
        "total_predictions": total,
        "won": won,
        "lost": lost,
        "pending": pending,
        "win_rate": win_rate,
        "total_stake": round(total_stake, 2),
        "total_profit": round(total_profit, 2),
        "roi": roi
    }


@router.get("/stats/detailed")
async def get_detailed_stats(current_user: dict = Depends(get_current_user)):
    """Get detailed statistics with streaks and records"""
    parlays = await db.parlays.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    won = sum(1 for p in parlays if p.get("status") == "won")
    lost = sum(1 for p in parlays if p.get("status") == "lost")
    pending = sum(1 for p in parlays if p.get("status") == "pending")
    
    total_stake = sum(p.get("stake", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    total_profit = sum(p.get("actual_profit", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    
    win_rate = round((won / (won + lost) * 100), 1) if (won + lost) > 0 else 0
    roi = round((total_profit / total_stake * 100), 1) if total_stake > 0 else 0
    
    # Calculate streaks
    current_streak = 0
    streak_type = None
    best_win = 0
    worst_loss = 0
    
    resolved = [p for p in parlays if p.get("status") in ["won", "lost"]]
    
    for p in resolved:
        profit = p.get("actual_profit", 0) or 0
        if profit > best_win:
            best_win = profit
        if profit < worst_loss:
            worst_loss = profit
    
    # Calculate current streak
    for p in resolved:
        if streak_type is None:
            streak_type = p.get("status")
            current_streak = 1
        elif p.get("status") == streak_type:
            current_streak += 1
        else:
            break
    
    return {
        "won": won,
        "lost": lost,
        "pending": pending,
        "total": len(parlays),
        "win_rate": win_rate,
        "roi": roi,
        "total_stake": round(total_stake, 2),
        "total_profit": round(total_profit, 2),
        "current_streak": current_streak,
        "streak_type": streak_type or "none",
        "best_win": round(best_win, 2),
        "worst_loss": round(worst_loss, 2)
    }
