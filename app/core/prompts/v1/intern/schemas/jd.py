from typing import List
from pydantic import BaseModel


class JDRequirement(BaseModel):
    education: List[str] = []
    technical_skills: List[str] = []
    experience: List[str] = []


class JDInformation(BaseModel):
    position_title: str
    responsibilities: List[str] = []
    requirements: JDRequirement
