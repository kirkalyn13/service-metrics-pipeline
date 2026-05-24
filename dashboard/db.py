import os
from sqlalchemy import create_engine

PG_HOST     = os.getenv("PG_HOST", "localhost")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_DB       = os.getenv("PG_DB", "service_metrics_db")
PG_USER     = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_SCHEMA   = os.getenv("PG_SCHEMA", "public")

def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )