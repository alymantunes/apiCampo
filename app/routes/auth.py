from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.controllers.auth_controller import (
    autenticar_usuario,
    criar_token,
    criar_refresh_token,
    verificar_refresh_token
)

router = APIRouter()

class LoginModel(BaseModel):
    usuario: str
    senha: str

class RefreshModel(BaseModel):
    refresh_token: str

@router.post("/login")
def login(dados: LoginModel):
    login = autenticar_usuario(dados.usuario, dados.senha)
    if not login:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    token = criar_token(login)
    refresh = criar_refresh_token(login)
    return {"access_token": token, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/refresh")
def refresh_token(dados: RefreshModel):
    try:
        payload = verificar_refresh_token(dados.refresh_token)
        login = {"nomeusu": payload["sub"], "codusu": payload.get("codusu", 0)}
        new_token = criar_token(login)
        return {"access_token": new_token, "token_type": "bearer"}
    except:
        raise HTTPException(status_code=403, detail="Refresh token inválido")
    
@router.get("/")
def root():
    return {"mensagem": "API funcionando!"}  