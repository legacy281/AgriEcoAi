from pydantic import BaseModel
from typing import Union


class ScoreRequest(BaseModel):
    """Request schema for scoring a job description and a CV"""

    jdPath: str
    cvPath: str


class ScoreResponse(BaseModel):
    """Response schema for scoring a job description and a CV"""

    university: Union[str, None] = None
    major: Union[str, None] = None
    GPA: Union[float, None] = None
    languages: Union[str, None] = None
    experience: Union[str, None] = None
    score: Union[float, None] = None
