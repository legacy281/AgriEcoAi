import os
import requests
import shutil
from fastapi import APIRouter, File, UploadFile

from app.api.services.extract_service import ExtractService
from app.api.services.scoring_service import ScoreService
from app.api.schemas.score import ScoreRequest, ScoreResponse
from app.api.responses.base import BaseResponse
from app.core.config import ALLOW_FILE_CONTENT_TYPES, OUTPUT_FOLDER
from app.logger.logger import custom_logger

router = APIRouter()
extract_service = ExtractService()
matching_service = ScoreService()

@router.post("/")
async def scan_cv():
    """Scores a CV based on a job description"""
    return {"score": 85}