"""Main application entrypoint for A.D.A.N.

AI Data Analysis & Verification Network (PS08: Proof-Carrying Data Analyst)
Phase 1 Foundation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG,
)

# CORS configuration to allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes under /api and also provide root /health directly
app.include_router(api_router, prefix="/api")
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root_info() -> dict:
    """Project metadata and system entrypoint."""
    return {
        "project": "A.D.A.N.",
        "full_name": "AI Data Analysis & Verification Network",
        "track": "PS08: Proof-Carrying Data Analyst (Agentic GenAI)",
        "phase": "Phase 3 - Question Analysis & Answerability",
        "docs_url": "/docs",
        "health_check": "/health",
        "datasets_endpoint": "/api/datasets",
        "questions_endpoint": "/api/questions/analyze",
    }
