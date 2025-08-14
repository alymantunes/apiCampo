import cx_Oracle
import hashlib
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def gerar_hash_interno(usuario, senha):
    texto = (usuario).upper() + senha
    return hashlib.md5(texto.encode()).hexdigest()

def validar_usuario(usuario, senha):
    hash_interno = gerar_hash_interno(usuario, senha)
    # logger.debug(f"Hash gerado para {usuario}: {hash_interno}")
    try:
        conn = cx_Oracle.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN")
        )
        cur = conn.cursor()
        cur.execute(
            """
            SELECT CODUSU, NOMEUSU FROM TSIUSU
            WHERE UPPER(NOMEUSU) = UPPER(:usuario)
              AND INTERNO = :interno
            """,
            {'usuario': usuario, 'interno': hash_interno}
        )
        row = cur.fetchone()
        logger.debug(f"Resultado da query: {row}")
        cur.close()
        conn.close()
        if row:
            logger.info(f"Login OK: {usuario}")
            return {"codusu": row[0], "nomeusu": row[1]}
        else:
            logger.warning(f"Tentativa inválida de login: {usuario}")
            return None
    except Exception as e:
        logger.error(f"Erro ao validar usuário: {e}")
        return None