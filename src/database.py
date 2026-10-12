"""Configuração compartilhada; credenciais ficam fora do código."""
import os
from sqlalchemy import URL, create_engine


def get_engine():
    if os.getenv("DATABASE_URL"):
        return create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    return create_engine(URL.create(
        "postgresql+psycopg2", username=os.getenv("POSTGRES_USER", "iot"),
        password=os.environ["POSTGRES_PASSWORD"], host=os.getenv("DB_HOST", "localhost"),
        port=5432, database=os.getenv("POSTGRES_DB", "iot")), pool_pre_ping=True)
