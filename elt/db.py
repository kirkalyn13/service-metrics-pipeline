import os
import pandas as pd
from sqlalchemy import create_engine, text

PG_HOST     = os.getenv("PG_HOST", "host.docker.internal")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_DB       = os.getenv("PG_DB", "service_metrics_db")
PG_USER     = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_SCHEMA   = os.getenv("PG_SCHEMA", "public")

ENGINE = create_engine(
        f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )

def ensure_partitioned_table(table: str, table_ddl: str, partition_ddl: str, years: list) -> None:
    """Create table partitions"""
    with ENGINE.begin() as conn:
        # Create parent partitioned table
        conn.execute(text(table_ddl.format(schema=PG_SCHEMA, table=table)))

        # Create a partition for each year found in the data
        for year in years:
            conn.execute(text(partition_ddl.format(
                schema=PG_SCHEMA,
                table=table,
                year=year,
                next_year=year + 1,
            )))
    print(f"  Partitions ensured for years: {years} -> {PG_SCHEMA}.{table}")


def load_to_postgres(df: pd.DataFrame, table: str) -> None:
    """Load dataframe to postgresql database"""
    df.to_sql(
        name=table,
        con=ENGINE,
        schema=PG_SCHEMA,
        if_exists="append",
        index=False,
    )
    print(f"  Loaded {len(df)} rows -> {PG_SCHEMA}.{table}")