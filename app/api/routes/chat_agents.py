import requests
from fastapi import APIRouter
from pydantic import BaseModel

from app.api.services.agents.agri_chat import ChatBackend
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger

from app.api.services.agents.price_agent import PriceAgent
from app.api.services.agents.recommend_agent import RecommendAgent
from app.api.services.agents.demand_agent import DemandAgent

router = APIRouter()

# ====== Agents ======
available_agents = {
    "price_agent": PriceAgent(),
    "recommend_agent": RecommendAgent(),
    "demand_agent": DemandAgent()
}

chat_backend = ChatBackend(
    available_agents=available_agents,
    product_name="gạo",
    region_name="vietnam"
)

# Request model
class ChatRequest(BaseModel):
    message: str


@router.post("")
async def general_chat(payload: ChatRequest):
    """
    General AI chat using agent routing (no session).
    """
    try:
        result = chat_backend.chat(
            user_input=payload.message
        )

        return BaseResponse.success_response(
            message="Chat success",
            data=result
        )

    except requests.RequestException as e:
        return BaseResponse.error_response(
            message=f"Request error: {e}"
        )

    except Exception as e:
        custom_logger.exception(e)
        return BaseResponse.error_response(
            message=f"Unexpected error: {e}"
        )
