import psycopg
from contextlib import contextmanager
from config import PG_DSN

@contextmanager
    def pg_conn():
    conn = psycopg.connect(PG_DSN)
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
        else:
            conn.commit()
    finally:
        conn.close()