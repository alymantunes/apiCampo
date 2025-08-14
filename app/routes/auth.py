from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.controllers.auth_controller import (
    autenticar_usuario,
    criar_token,
    criar_refresh_token,
    verificar_refresh_token,
)

router = APIRouter(prefix="", tags=["auth"])

# ---- Schemas ----
class LoginModel(BaseModel):
    usuario: str = Field(..., min_length=1)
    senha: str = Field(..., min_length=1)

class RefreshModel(BaseModel):
    refresh_token: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---- Endpoints ----
@router.post("/login", response_model=TokenPair, status_code=status.HTTP_200_OK)
def login(dados: LoginModel) -> TokenPair:
    usuario = autenticar_usuario(dados.usuario, dados.senha)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
        )

    # ⚠️ garanta que 'usuario' tenha 'codusu' e um identificador para 'sub'
    # ex.: usuario = {"codusu": 397, "nomeusu": "SUP"} vindo do seu controller
    token = criar_token(usuario)              # deve incluir {"sub": ..., "codusu": ...}
    refresh = criar_refresh_token(usuario)    # idem, se precisar

    return TokenPair(access_token=token, refresh_token=refresh)

@router.post("/refresh", response_model=AccessToken, status_code=status.HTTP_200_OK)
def refresh_token(dados: RefreshModel) -> AccessToken:
    try:
        payload = verificar_refresh_token(dados.refresh_token)
        user = {"codusu": payload.get("codusu"), "nomeusu": payload.get("sub")}
        if user["codusu"] is None:
            raise HTTPException(status_code=400, detail="Refresh token sem 'codusu'")
        new_token = criar_token(user)
        return AccessToken(access_token=new_token)
    except HTTPException:
        # repassa erros já padronizados
        raise
    except Exception:
        # em produção, logue a exceção
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Refresh token inválido",
        )
