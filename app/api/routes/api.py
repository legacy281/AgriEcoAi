"""API Routes."""

from fastapi import APIRouter

from app.api.routes import chat_router, scan_cv_router ,chat_agents

app = APIRouter()

app.include_router(chat_router.router, tags=["Chat"], prefix="/chat")
app.include_router(scan_cv_router.router, tags=["Extract post"], prefix="/extract-post")
app.include_router(scan_cv_router.router, tags=["embedding post"], prefix="/embedding-post")
app.include_router(
    chat_agents.router,
    tags=["Chat Agents"],
    prefix="/chat-agents"
)
app.include_router(scan_cv_router.router, tags=["Recommendation"], prefix="/recomnnend") 