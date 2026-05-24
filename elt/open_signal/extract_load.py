"""
ELT Script: Open Signal Stats — XLSX -> PostgreSQL
Splits data by Technology (3G / 4G) into separate tables.
Raw tables are partitioned by year on report_end_date.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

DATA_PATH   = os.getenv("DATA_PATH", "/data")
PG_HOST     = os.getenv("PG_HOST", "host.docker.internal")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_DB       = os.getenv("PG_DB", "service_metrics_db")
PG_USER     = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_SCHEMA   = os.getenv("PG_SCHEMA", "public")

COLUMN_MAP = {
    "Aggregation":                   "aggregation",
    "Day of Report End Date":        "report_end_date",
    "Network Name Mapped":           "network_name",
    "Technology":                    "technology",
    "Location Category":             "location_category",
    "Area":                          "area",
    "Location":                      "location",
    "Availability Devices":          "availability_devices",
    "Availability Mean":             "availability_mean",
    "Availability Readings":         "availability_readings",
    "Download Devices":              "download_devices",
    "Download Mean":                 "download_mean",
    "Download Readings":             "download_readings",
    "Latency Devices":               "latency_devices",
    "Latency Mean":                  "latency_mean",
    "Latency Readings":              "latency_readings",
    "Number of Records":             "number_of_records",
    "Upload Devices":                "upload_devices",
    "Upload Mean":                   "upload_mean",
    "Upload Readings":               "upload_readings",
    "Videoexperience Devices":       "videoexperience_devices",
    "Videoexperience Mean":          "videoexperience_mean",
    "Videoexperience Readings":      "videoexperience_readings",
    "Voiceappexperience Devices":    "voiceappexperience_devices",
    "Voiceappexperience Mean":       "voiceappexperience_mean",
    "Voiceappexperience Readings":   "voiceappexperience_readings",
}

TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {schema}.{table} (
        aggregation                  INTEGER,
        report_end_date              DATE NOT NULL,
        network_name                 TEXT,
        technology                   TEXT,
        location_category            TEXT,
        area                         TEXT,
        location                     TEXT,
        availability_devices         DOUBLE PRECISION,
        availability_mean            DOUBLE PRECISION,
        availability_readings        DOUBLE PRECISION,
        download_devices             DOUBLE PRECISION,
        download_mean                DOUBLE PRECISION,
        download_readings            DOUBLE PRECISION,
        latency_devices              DOUBLE PRECISION,
        latency_mean                 DOUBLE PRECISION,
        latency_readings             DOUBLE PRECISION,
        number_of_records            INTEGER,
        upload_devices               DOUBLE PRECISION,
        upload_mean                  DOUBLE PRECISION,
        upload_readings              DOUBLE PRECISION,
        videoexperience_devices      DOUBLE PRECISION,
        videoexperience_mean         DOUBLE PRECISION,
        videoexperience_readings     DOUBLE PRECISION,
        voiceappexperience_devices   DOUBLE PRECISION,
        voiceappexperience_mean      DOUBLE PRECISION,
        voiceappexperience_readings  DOUBLE PRECISION
    ) PARTITION BY RANGE (report_end_date);
"""

PARTITION_DDL = """
    CREATE TABLE IF NOT EXISTS {schema}.{table}_y{year}
    PARTITION OF {schema}.{table}
    FOR VALUES FROM ('{year}-01-01') TO ('{next_year}-01-01');
"""


def extract() -> pd.DataFrame:
    df = pd.read_excel(DATA_PATH)
    df.rename(columns=COLUMN_MAP, inplace=True)
    df["report_end_date"] = pd.to_datetime(df["report_end_date"]).dt.date
    return df


def ensure_partitioned_table(engine, table: str, years: list) -> None:
    with engine.begin() as conn:
        # Create parent partitioned table
        conn.execute(text(TABLE_DDL.format(schema=PG_SCHEMA, table=table)))

        # Create a partition for each year found in the data
        for year in years:
            conn.execute(text(PARTITION_DDL.format(
                schema=PG_SCHEMA,
                table=table,
                year=year,
                next_year=year + 1,
            )))
    print(f"  Partitions ensured for years: {years} -> {PG_SCHEMA}.{table}")


def load_to_postgres(df: pd.DataFrame, table: str, engine) -> None:
    df.to_sql(
        name=table,
        con=engine,
        schema=PG_SCHEMA,
        if_exists="append",
        index=False,
    )
    print(f"  Loaded {len(df)} rows -> {PG_SCHEMA}.{table}")


def run():
    engine = create_engine(
        f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )

    print("Extracting from XLSX…")
    df = extract()

    technologies = df["technology"].unique()
    print(f"Technologies found: {list(technologies)}")

    for tech in technologies:
        tech_key = tech.lower().replace(" ", "_")
        table    = f"raw_open_signal_{tech_key}"
        subset   = df[df["technology"] == tech].reset_index(drop=True)
        years    = sorted(subset["report_end_date"].apply(lambda d: d.year).unique().tolist())

        print(f"Ensuring partitioned table for {tech}…")
        ensure_partitioned_table(engine, table, years)

        print(f"Loading {tech} data…")
        load_to_postgres(subset, table, engine)

    print("Done.")


if __name__ == "__main__":
    run()