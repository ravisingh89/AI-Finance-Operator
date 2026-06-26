from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from app.api.middleware.auth import get_current_user
from app.db.database import save_report, set_status, get_status
from app.agents.orchestrator import run_pipeline
import uuid

router = APIRouter()

MAX_SIZE = 15 * 1024 * 1024  # 15 MB

@router.post("/upload")
async def upload_statement(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    currency: str = Form("AED"),
    region: str   = Form("UAE"),
    user = Depends(get_current_user),
):
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(400, "Empty file.")
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(400, "File too large. Max 15 MB.")

    # Detect type from filename
    fname = (file.filename or "").lower()
    if fname.endswith(".pdf"):
        content_type = "application/pdf"
    elif fname.endswith(".csv"):
        content_type = "text/csv"
    elif fname.endswith(".xlsx"):
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        content_type = file.content_type or "text/csv"

    stmt_id = str(uuid.uuid4())
    set_status(stmt_id, "processing")

    background_tasks.add_task(
        _process, stmt_id, file_bytes, content_type,
        user["id"], currency, region
    )

    return {"statement_id": stmt_id, "status": "processing"}


@router.get("/{statement_id}/status")
async def get_stmt_status(
    statement_id: str,
    user = Depends(get_current_user),
):
    status = get_status(statement_id)
    return {"statement_id": statement_id, "status": status}


async def _process(stmt_id, file_bytes, content_type, user_id, currency, region):
    try:
        print(f"[INFO] Processing {stmt_id} for user {user_id}")
        transactions = _parse(file_bytes, content_type, currency)
        print(f"[INFO] Parsed {len(transactions)} transactions")

        report = run_pipeline(transactions, region=region, currency=currency)
        print(f"[INFO] Pipeline done. Waste: {report['summary']['waste_score']} Savings: {report['summary']['savings_score']}")

        save_report(user_id, stmt_id, report)
        set_status(stmt_id, "done")
        print(f"[INFO] Report saved for user {user_id}")

    except Exception as e:
        import traceback
        print(f"[ERROR] Processing failed: {e}")
        traceback.print_exc()
        set_status(stmt_id, "failed")


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
