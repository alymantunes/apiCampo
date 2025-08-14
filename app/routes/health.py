
from fastapi import APIRouter
import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

@router.get("/health")
def health_check():
    try:
        conn = cx_Oracle.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN")
        )
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM DUAL")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return {"status": "ok", "db": result[0]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
