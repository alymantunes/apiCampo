
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError
import os
from app.config.rotas_liberadas import ROTAS_LIBERADAS

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ROTAS_LIBERADAS:
            return await call_next(request)

        auth_header = request.headers.get("authorization")
        if not auth_header:
            return JSONResponse(status_code=401, content={"detail": "Token não enviado"})

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
            request.state.user = payload
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Token inválido"})

        return await call_next(request)
