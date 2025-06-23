import os
from fastapi import  Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from typing import Callable


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        
        url_path = request.url.path
        if '/api' not in url_path:
            return await call_next(request)
        # Get the authorization header
        auth_header = request.headers.get("Authorization")
    
        # Check if the header exists and starts with "Bearer"
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail":"Authorization header missing or invalid"},
            )

        # Extract the token from the header
        token = auth_header[7:]  # Skip the "Bearer " prefix

        try:
            # Decode and verify the JWT token
            payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
            request.state.user = payload  # Attach user info to request state

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail":"Token has expired"},
            )
        except jwt.InvalidKeyError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail":"Invalid token"},
            )

        # Proceed with the request if the token is valid
        response = await call_next(request)
        return response