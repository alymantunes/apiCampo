import os
import cx_Oracle
from loguru import logger

# Pool simples (ajuste min/max conforme carga)
POOL = cx_Oracle.SessionPool(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=os.getenv("DB_DSN"),
    min=1, max=5, increment=1, threaded=True,
    encoding="UTF-8", nencoding="UTF-8",
)

SQL_PENDENTES = """
SELECT
    lib.NUCHAVE,
    NVL(NVL(CAB.NUNOTA,ITE.NUNOTA),FIN.NUNOTA) NRUNICONOTA,
    NOTA.CODEMP,
    NOTA.CODVEND,
    VEN.APELIDO vendedor,
    NOTA.CODPARC,
    PAR.RAZAOSOCIAL,
    PAR.NOMEPARC ,
    LIB.TABELA,
    eve.EVENTO,
    eve.DESCRICAO,
    lib.CODUSUSOLICIT,
    USOL.NOMEUSU USUSOLICIT,
    lib.DHSOLICIT,
    lib.VLRATUAL,
    lib.VLRLIMITE,
    lib.OBSERVACAO
FROM tsilib lib
LEFT JOIN TGFCAB CAB ON LIB.TABELA = 'TGFCAB' AND LIB.NUCHAVE = CAB.NUNOTA
LEFT JOIN TGFITE ITE ON LIB.TABELA  = 'TGFITE' AND LIB.NUCHAVE = ITE.NUNOTA AND ITE.SEQUENCIA = LIB.SEQUENCIA 
LEFT JOIN TGFFIN FIN ON LIB.TABELA  = 'TGFFIN' AND LIB.NUCHAVE = FIN.NUFIN
LEFT JOIN TGFCAB NOTA ON NOTA.NUNOTA = NVL(NVL(CAB.NUNOTA,ITE.NUNOTA),FIN.NUNOTA) 
LEFT JOIN TGFPAR PAR ON PAR.CODPARC = NOTA.CODPARC
LEFT JOIN TGFVEN VEN ON VEN.CODVEND = NOTA.CODVEND
JOIN TSIUSU USOL ON USOL.CODUSU = LIB.CODUSUSOLICIT 
JOIN tsilim lim
  ON (lib.codusulib = lim.codusu OR lib.codusulib = 0)
 AND lib.evento = lim.evento
JOIN vgflibeve eve
  ON eve.evento = lib.evento
WHERE
      (lim.codusu = :codusu
       OR lim.codusu IN (SELECT spl.codusu FROM tsisupl spl WHERE spl.codususupl = :codusu))
  AND lib.vlratual <= lim.limite
  AND lib.dhlib IS NULL
ORDER BY lib.dhsolicit DESC
"""

def listar_liberacoes_pendentes(codusu):
    """
    Retorna lista de liberações pendentes visíveis para 'codusu'.
    """
    conn = POOL.acquire()
    cur = conn.cursor()
    try:
        cur.arraysize = 500
        cur.execute(SQL_PENDENTES, {"codusu": codusu})
        cols = [d[0].lower() for d in cur.description]  # nomes de colunas
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        logger.debug(f"{len(rows)} pendência(s) para codusu={codusu}")
        return rows
    except cx_Oracle.DatabaseError as e:
        err, = e.args
        logger.error(f"Oracle error: ORA-{getattr(err,'code','?')} {getattr(err,'message',e)}")
        return []
    finally:
        try:
            cur.close()
        finally:
            POOL.release(conn)
