from app.models.liberacoes_model import listar_liberacoes_pendentes

def get_pendentes(codusu: int):
    return listar_liberacoes_pendentes(codusu)
