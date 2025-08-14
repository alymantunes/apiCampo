# app/routes/liberacoes.py
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.deps.auth import get_current_user
from app.controllers.liberacoes_controller import get_pendentes

router = APIRouter(prefix="", tags=["liberacoes"])

class LiberacaoPendente(BaseModel):
    nuchave: int
    NRUNICONOTA: Optional[int] = Field(None, alias="nruniconota")
    codemp: int
    codvend: int
    vendedor: Optional[str] = None
    codparc: int
    razaosocial: Optional[str] = None
    nomeparc: Optional[str] = None
    tabela: str
    evento: str
    descricao: str
    codususolicit: int
    dhsolicit: Optional[datetime] = None
    vlratual: Optional[Decimal] = Field(None)
    vlrlimite: Optional[Decimal] = Field(None)
    observacao: Optional[str] = None

@router.get("/pendentes", response_model=List[LiberacaoPendente])  # <- barra inicial!
def listar_pendentes(user: dict = Depends(get_current_user)):
    codusu = int(user["codusu"])
    data = get_pendentes(codusu)
    if data is None:
        raise HTTPException(500, "Erro ao buscar liberações pendentes")
    return data
