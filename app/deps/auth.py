from fastapi import Header, HTTPException, status
from app.controllers.auth_controller import verificar_token

def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Lê Authorization: Bearer <token>, valida e retorna o payload (precisa ter 'codusu').
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabeçalho Authorization ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato inválido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    try:
        payload = verificar_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )

    if "codusu" not in payload:
        raise HTTPException(status_code=400, detail="Token não contém 'codusu'")

    return payload
