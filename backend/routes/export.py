"""
Export routes for Excel and PDF generation
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import io

from services.auth_service import get_current_user
from services.export_service import generate_parlays_excel, generate_stats_pdf
from config.database import db

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/excel")
async def export_to_excel(current_user: dict = Depends(get_current_user)):
    """Export parlays and stats to Excel file"""
    # Get parlays
    parlays = await db.parlays.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    # Calculate stats
    won = sum(1 for p in parlays if p.get("status") == "won")
    lost = sum(1 for p in parlays if p.get("status") == "lost")
    pending = sum(1 for p in parlays if p.get("status") == "pending")
    
    total_stake = sum(p.get("stake", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    total_profit = sum(p.get("actual_profit", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    
    win_rate = round((won / (won + lost) * 100), 1) if (won + lost) > 0 else 0
    roi = round((total_profit / total_stake * 100), 1) if total_stake > 0 else 0
    
    # Find best win and worst loss
    best_win = 0
    worst_loss = 0
    current_streak = 0
    streak_type = "none"
    
    resolved = [p for p in parlays if p.get("status") in ["won", "lost"]]
    for p in resolved:
        profit = p.get("actual_profit", 0) or 0
        if profit > best_win:
            best_win = profit
        if profit < worst_loss:
            worst_loss = profit
    
    for p in resolved:
        if streak_type == "none":
            streak_type = p.get("status")
            current_streak = 1
        elif p.get("status") == streak_type:
            current_streak += 1
        else:
            break
    
    stats = {
        "total": len(parlays),
        "won": won,
        "lost": lost,
        "pending": pending,
        "win_rate": win_rate,
        "roi": roi,
        "total_stake": round(total_stake, 2),
        "total_profit": round(total_profit, 2),
        "best_win": round(best_win, 2),
        "worst_loss": round(worst_loss, 2),
        "current_streak": current_streak,
        "streak_type": streak_type
    }
    
    # Generate Excel
    excel_bytes = generate_parlays_excel(parlays, stats)
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=sportsbetai_historial.xlsx"
        }
    )


@router.get("/pdf")
async def export_to_pdf(current_user: dict = Depends(get_current_user)):
    """Export stats to PDF report"""
    # Get parlays
    parlays = await db.parlays.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    # Calculate stats
    won = sum(1 for p in parlays if p.get("status") == "won")
    lost = sum(1 for p in parlays if p.get("status") == "lost")
    pending = sum(1 for p in parlays if p.get("status") == "pending")
    
    total_stake = sum(p.get("stake", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    total_profit = sum(p.get("actual_profit", 0) or 0 for p in parlays if p.get("status") in ["won", "lost"])
    
    win_rate = round((won / (won + lost) * 100), 1) if (won + lost) > 0 else 0
    roi = round((total_profit / total_stake * 100), 1) if total_stake > 0 else 0
    
    best_win = 0
    worst_loss = 0
    for p in parlays:
        if p.get("status") in ["won", "lost"]:
            profit = p.get("actual_profit", 0) or 0
            if profit > best_win:
                best_win = profit
            if profit < worst_loss:
                worst_loss = profit
    
    stats = {
        "total": len(parlays),
        "won": won,
        "lost": lost,
        "pending": pending,
        "win_rate": win_rate,
        "roi": roi,
        "total_stake": round(total_stake, 2),
        "total_profit": round(total_profit, 2),
        "best_win": round(best_win, 2),
        "worst_loss": round(worst_loss, 2)
    }
    
    # Generate PDF
    pdf_bytes = generate_stats_pdf(stats, parlays)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=sportsbetai_reporte.pdf"
        }
    )
