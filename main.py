from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.protected import router as protected_router
from app.middleware.auth_middleware import AuthMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(AuthMiddleware)
# ⬇️ Adicione isso aqui logo após criar o app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar todas as rotas
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(protected_router)
