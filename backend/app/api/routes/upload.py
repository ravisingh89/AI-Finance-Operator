from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, select
from app.db.database import get_db, Statement, Transaction, FinancialReport
from app.api.middleware.auth import get_current_user
from app.services.supabase_service import SupabaseService
from app.agents.orchestrator import run_pipeline
import uuid, json

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/plain",
}
MAX_SIZE = 15 * 1024 * 1024  # 15 MB


@router.post("/upload")
async def upload_statement(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    currency: str = Form("AED"),
    region: str   = Form("UAE"),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}. Use PDF, CSV, or XLSX.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(400, "File too large. Max 15 MB.")

    # Upload to Supabase Storage
    storage = SupabaseService()
    file_url = storage.upload_file(file_bytes, file.filename, user["id"])

    # Create statement record
    stmt_id = str(uuid.uuid4())
    await db.execute(
        insert(Statement).values(
            id=stmt_id, user_id=user["id"],
            file_name=file.filename, file_url=file_url,
            file_type=file.content_type, status="processing"
        )
    )
    await db.commit()

    # Run analysis in background
    background_tasks.add_task(
        _process, stmt_id, file_bytes, file.content_type, user["id"], currency, region
    )

    return {"statement_id": stmt_id, "status": "processing"}


@router.get("/{statement_id}/status")
async def get_status(
    statement_id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    result = await db.execute(
        select(Statement).where(Statement.id == statement_id, Statement.user_id == user["id"])
    )
    stmt = result.scalar_one_or_none()
    if not stmt:
        raise HTTPException(404, "Statement not found")
    return {"statement_id": statement_id, "status": stmt.status}


async def _process(stmt_id, file_bytes, content_type, user_id, currency, region):
    """Background task: parse → analyze → save."""
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            # Parse
            transactions = _parse(file_bytes, content_type, currency)

            # Save raw transactions
            for tx in transactions:
                await db.execute(insert(Transaction).values(
                    id=str(uuid.uuid4()),
                    statement_id=stmt_id, user_id=user_id,
                    date=tx.get("date"), merchant=tx.get("merchant"),
                    amount=tx.get("amount"), currency=tx.get("currency"),
                    type=tx.get("type"), description=tx.get("description"),
                ))

            # Run full AI pipeline
            report = run_pipeline(transactions, region=region, currency=currency)

            # Update transaction categories
            for tx in report["classified_transactions"]:
                await db.execute(
                    update(Transaction)
                    .where(Transaction.statement_id == stmt_id,
                           Transaction.merchant == tx.get("merchant"),
                           Transaction.amount == tx.get("amount"))
                    .values(category=tx.get("category"),
                            category_confidence=tx.get("confidence"))
                )

            # Save report
            await db.execute(insert(FinancialReport).values(
                id=str(uuid.uuid4()),
                user_id=user_id, statement_id=stmt_id,
                report_data=report,
                waste_score=report["summary"]["waste_score"],
                savings_score=report["summary"]["savings_score"],
            ))

            await db.execute(
                update(Statement).where(Statement.id == stmt_id).values(status="done")
            )
            await db.commit()

        except Exception as e:
            await db.execute(
                update(Statement).where(Statement.id == stmt_id).values(status="failed")
            )
            await db.commit()
            print(f"[ERROR] Processing failed for {stmt_id}: {e}")


def _parse(file_bytes: bytes, content_type: str, currency: str) -> list:
    if "pdf" in content_type:
        from app.parsers.pdf_parser import PDFParser
        result = PDFParser().parse(file_bytes, currency)
    elif "csv" in content_type or "text/plain" in content_type:
        from app.parsers.csv_parser import CSVParser
        result = CSVParser().parse(file_bytes, currency)
    else:
        from app.parsers.excel_parser import ExcelParser
        result = ExcelParser().parse(file_bytes, currency)
    return [t.model_dump() for t in result.transactions]
