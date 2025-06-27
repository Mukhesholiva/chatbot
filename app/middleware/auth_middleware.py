from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from ..core.config import settings
from datetime import datetime

async def token_expiration_middleware(request: Request, call_next):
    # Skip middleware for login and refresh endpoints
    if request.url.path in ["/api/v1/auth/login", "/api/v1/auth/refresh"]:
        return await call_next(request)

    try:
        # Get the authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)

        # Extract the token
        token = auth_header.split(" ")[1]
        
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp")
        
        if exp:
            # Only return 401 if token is actually expired
            if datetime.utcnow().timestamp() > exp:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Token has expired",
                        "code": "TOKEN_EXPIRED"
                    }
                )

    except JWTError:
        # If token is invalid, let the normal authentication handle it
        pass

    return await call_next(request) 