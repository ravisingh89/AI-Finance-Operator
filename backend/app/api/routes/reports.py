from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db, FinancialReport, Transaction
from app.api.middleware.auth import get_current_user

router = APIRouter()


@router.get("/reports/latest")
async def get_latest_report(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    result = await db.execute(
        select(FinancialReport)
        .where(FinancialReport.user_id == user["id"])
        .order_by(FinancialReport.created_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "No report found. Upload a statement first.")
    return {"statement_id": str(report.statement_id), "report": report.report_data}


@router.get("/reports/history")
async def get_report_history(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    result = await db.execute(
        select(FinancialReport)
        .where(FinancialReport.user_id == user["id"])
        .order_by(FinancialReport.created_at.desc())
        .limit(10)
    )
    reports = result.scalars().all()
    return {"reports": [{"id": str(r.id), "created_at": str(r.created_at),
                          "waste_score": r.waste_score, "savings_score": r.savings_score}
                         for r in reports]}


@router.get("/transactions")
async def get_transactions(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user["id"])
        .order_by(Transaction.date.desc())
        .limit(200)
    )
    txs = result.scalars().all()
    return {"transactions": [
        {"date": t.date, "merchant": t.merchant, "amount": t.amount,
         "currency": t.currency, "type": t.type, "category": t.category}
        for t in txs
    ]}
