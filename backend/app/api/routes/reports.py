from fastapi import APIRouter, Depends, HTTPException
from app.api.middleware.auth import get_current_user
from app.db.database import get_report

router = APIRouter()

@router.get("/reports/latest")
async def get_latest_report(user = Depends(get_current_user)):
    data = get_report(user["id"])
    if not data:
        raise HTTPException(404, "No report found. Upload a statement first.")
    return {"statement_id": data["statement_id"], "report": data["report"]}

@router.get("/reports/history")
async def get_report_history(user = Depends(get_current_user)):
    data = get_report(user["id"])
    if not data:
        return {"reports": []}
    return {"reports": [{
        "id":            data["statement_id"],
        "created_at":    data.get("created_at", ""),
        "waste_score":   data["report"]["summary"]["waste_score"],
        "savings_score": data["report"]["summary"]["savings_score"],
    }]}

@router.get("/transactions")
async def get_transactions(user = Depends(get_current_user)):
    data = get_report(user["id"])
    if not data:
        return {"transactions": []}
    txs = data["report"].get("classified_transactions", [])
    return {"transactions": txs[:200]}
