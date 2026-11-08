"""Bearer-token guard for the MCP endpoint."""
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

def _expected_token() -> str:
    return os.environ.get("MCP_AUTH_TOKEN", "")

def verify_token(authorization: str | None) -> bool:
    token = _expected_token()
    if not token:
        return True  # auth disabled if token not configured (local dev only)
    if not authorization or not authorization.startswith("Bearer "):
        return False
    return authorization.removeprefix("Bearer ").strip() == token

class BearerTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Only guard MCP paths; leave /docs, /openapi.json, /health open
        if request.url.path.startswith("/mcp"):
            if not verify_token(request.headers.get("authorization")):
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)