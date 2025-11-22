"""API Routes."""

from fastapi import APIRouter

from app.api.routes import chat_router, scoring_router, scan_cv_router 

app = APIRouter()

app.include_router(chat_router.router, tags=["Chat"], prefix="/chat")
app.include_router(scoring_router.router, tags=["Scoring"], prefix="/scoring")
app.include_router(scan_cv_router.router, tags=["Extract post"], prefix="/extract-post")
app.include_router(scan_cv_router.router, tags=["Recommendation"], prefix="/recomnnend") 