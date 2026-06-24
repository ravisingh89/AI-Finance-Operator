from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import upload, analysis, reports, health

app = FastAPI(
    title="AI Finance Operator",
    version="1.0.0",
    description="Agentic AI personal finance analysis — UAE & India"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,   tags=["Health"])
app.include_router(upload.router,   prefix="/api/v1/statements", tags=["Statements"])
app.include_router(analysis.router, prefix="/api/v1/analysis",   tags=["Analysis"])
app.include_router(reports.router,  prefix="/api/v1",            tags=["Reports"])
