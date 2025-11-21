import requests
from fastapi import APIRouter

from app.api.services.chat_service import ChatService
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger

router = APIRouter()
chat_service = ChatService()


@router.post("")
async def general_chat(message: str):
    """General Chat."""

    try:
        print("okeinit")
        return chat_service.general_chat(message=message)

    except requests.RequestException as e:
        return BaseResponse.error_response(message=f"An error occurred: {e}")
    
    except Exception as e:
        custom_logger.exception(e)
        return BaseResponse.error_response(message=f"An error occurred: {e}")
