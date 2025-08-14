from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv
from app.models.user_model import validar_usuario

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

def autenticar_usuario(usuario: str, senha: str):
    login = validar_usuario(usuario, senha)
    return login

def criar_token(usuario: dict):
    payload = {
        "sub": usuario["nomeusu"],
        "codusu": usuario["codusu"],
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def criar_refresh_token(usuario: dict):
    payload = {
        "sub": usuario["nomeusu"],
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm=ALGORITHM)

def verificar_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def verificar_refresh_token(token: str):
    return jwt.decode(token, REFRESH_SECRET, algorithms=[ALGORITHM])