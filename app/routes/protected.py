from fastapi import APIRouter, Header, HTTPException, Depends
from app.controllers.auth_controller import verificar_token

router = APIRouter()

def get_current_user(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    payload = verificar_token(token)
    return payload

@router.get("/protegido")
def rota_protegida(user: dict = Depends(get_current_user)):
    return {"mensagem": f"Acesso permitido para {user['codusu']} - {user['sub']}"}