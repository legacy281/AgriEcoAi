"""Define config for project."""
from __future__ import annotations

import logging, sys

from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings


API_PREFIX = "/api"

VERSION = "0.0.0"

config = Config(".env")

DEBUG: bool = config("DEBUG", cast=bool, default=False)

APP_HOST: str = config("APP_HOST", cast=str, default="127.0.0.1")
APP_PORT: str = config("APP_PORT", cast=str, default="9001")

PROJECT_NAME: str = config("Recruitment System AI", default="Recruitment System AI")
ALLOWED_HOSTS: list[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)

OUTPUT_FOLDER: str = "app/resources/outputs"

LLM_API_KEY: str = config("LLM_API_KEY", cast=str, default="")
MODEL_NAME: str = config("MODEL_NAME", cast=str, default="gpt-3.5-turbo")

ALLOW_FILE_CONTENT_TYPES = [
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

# logging configuration

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
