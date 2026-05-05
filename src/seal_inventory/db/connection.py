import os
import pyodbc
from contextlib import contextmanager


def build_connection_string(db_name: str) -> str:
    trust = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "true").lower() in ("1", "true", "yes")

    return (
        f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
        f"SERVER={os.getenv('DB_HOST')},{os.getenv('DB_PORT')};"
        f"DATABASE={db_name};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"TrustServerCertificate={'yes' if trust else 'no'};"
    )


def create_connection(db_name: str):
    return pyodbc.connect(build_connection_string(db_name), timeout=10)


@contextmanager
def get_dwh_connection():
    conn = create_connection(os.getenv("DWH_DB_NAME"))
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_inventory_connection():
    conn = create_connection(os.getenv("INV_DB_NAME"))
    try:
        yield conn
    finally:
        conn.close()