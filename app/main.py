"""Start Application."""

import random
import string
import time

import uvicorn
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
import google.generativeai as genai
from fastapi.openapi.utils import get_openapi


from app.api.middlewares.check_key_middleware import CheckKeyMiddleware
from app.api.routes.api import app as api_router
from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.core.config import (
    ALLOWED_HOSTS,
    API_PREFIX,
    DEBUG,
    PROJECT_NAME,
    VERSION,
    APP_HOST,
    APP_PORT,
    LLM_API_KEY,
)
from app.logger.logger import custom_logger

API_KEY_NAME = "x-api-key"

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        API_KEY_NAME: {
            "type": "apiKey",
            "in": "header",
            "name": API_KEY_NAME
        }
    }
    openapi_schema["security"] = [{API_KEY_NAME: []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging All API request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Dispatch."""
        idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        custom_logger.info(
            f"rid={idem} start request {request.method} {request.url.path}"
        )
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)

        custom_logger.info(
            "rid=%s method=%s path=%s completed_in=%sms status_code=%s",
            idem,
            request.method,
            request.url.path,
            formatted_process_time,
            response.status_code,
        )

        return response


def get_application() -> FastAPI:
    """Get app."""
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(CheckKeyMiddleware)

    application.add_middleware(LoggingMiddleware)
    # application.add_middleware(GZipMiddleware, minimum_size=1000)
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router, prefix=API_PREFIX)

    genai.configure(api_key=LLM_API_KEY)

    return application


app = get_application()
app.openapi = lambda: custom_openapi(app)

if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=int(APP_PORT))
