from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import os

API_KEY = os.getenv("INTERNAL_API_KEY", "super_secret_key_123")

class CheckKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Cho phép các route public (nếu bạn muốn)
        public_paths = ["/docs", "/openapi.json", "/health"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        api_key = request.headers.get("x-api-key")

        if api_key != API_KEY:
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden: Invalid or missing API Key"},
            )

        # Cho phép request đi tiếp
        response = await call_next(request)
        return response
