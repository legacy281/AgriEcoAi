from typing import List, Union
from pydantic import BaseModel


class Certificates(BaseModel):
    toeic: Union[int, None] = None
    ielts: Union[float, None] = None
    others: List[str] = []


class CVInformation(BaseModel):
    university: Union[str, None] = None
    major: Union[str, None] = None
    gpa: Union[float, None] = None
    experiences: List[str] = []
    technical_skills: List[str] = []
    responsibilities: List[str] = []
    certificates: Certificates
    achievements: List[str] = []
    summary: Union[str, None] = None
