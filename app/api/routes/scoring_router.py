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


@router.post("/local", response_model=ScoreResponse)
async def score_cv(score_request: ScoreRequest):
    """Scores a CV based on a job description"""

    try:
        jd_file_path = score_request.jdPath
        cv_file_path = score_request.cvPath

        jd_info = extract_service.process_jd(jd_file_path)
        cv_info = extract_service.process_cv(cv_file_path)

        if not cv_info:
            return ScoreResponse()

        # Score the CV
        score = matching_service.score_cv(jd_info, cv_info.model_dump())

        cert_list = []
        if cv_info.certificates.toeic is not None:
            cert_list.append(f"TOEIC ({cv_info.certificates.toeic})")
        if cv_info.certificates.ielts is not None:
            cert_list.append(f"IELTS ({cv_info.certificates.ielts})")

        # Join the non-None certificate values into a single string
        languages = ", ".join(cert_list) if cert_list else None

        score_response = ScoreResponse(
            university=cv_info.university,
            major=cv_info.major,
            GPA=cv_info.gpa,
            languages=languages,
            experience=cv_info.summary,
            score=score,
        )

        return score_response

    except requests.RequestException as e:
        return BaseResponse.error_response(message=f"An error occurred: {e}")

    except Exception as e:
        custom_logger.exception(e)
        return BaseResponse.error_response(message=f"An error occurred: {e}")


@router.post("", response_model=ScoreResponse)
async def score_cv(
    jd: UploadFile = File(...), cv: UploadFile = File(...)
):
    """Scores a CV based on a job description"""

    try:
        # check file extension support
        if (
            jd.content_type not in ALLOW_FILE_CONTENT_TYPES
            or cv.content_type not in ALLOW_FILE_CONTENT_TYPES
        ):
            return BaseResponse.error_response(
                status_code=400, message="Unsupported file type"
            )

        jd_file_path = os.path.join(OUTPUT_FOLDER, jd.filename)
        cv_file_path = os.path.join(OUTPUT_FOLDER, cv.filename)

        # Save the file
        with open(jd_file_path, "wb") as jd_file:
            shutil.copyfileobj(jd.file, jd_file)

        with open(cv_file_path, "wb") as cv_file:
            shutil.copyfileobj(cv.file, cv_file)

        jd_info = extract_service.process_jd(jd_file_path)
        cv_info = extract_service.process_cv(cv_file_path)

        if not cv_info:
            return ScoreResponse()

        # Score the CV
        score = matching_service.calculate_score(
            jd_info.model_dump(), cv_info.model_dump()
        )

        cert_list = []
        if cv_info.certificates.toeic is not None:
            cert_list.append(f"TOEIC ({cv_info.certificates.toeic})")
        if cv_info.certificates.ielts is not None:
            cert_list.append(f"IELTS ({cv_info.certificates.ielts})")

        # Join certificate values into a single string
        languages = ", ".join(cert_list) if cert_list else None

        score_response = ScoreResponse(
            university=cv_info.university,
            major=cv_info.major,
            GPA=cv_info.gpa,
            languages=languages,
            experience=cv_info.summary,
            score=score,
        )

        return score_response

    except requests.RequestException as e:
        return BaseResponse.error_response(message=f"An error occurred: {e}")

    except Exception as e:
        custom_logger.exception(e)
        return BaseResponse.error_response(message=f"An error occurred: {e}")
