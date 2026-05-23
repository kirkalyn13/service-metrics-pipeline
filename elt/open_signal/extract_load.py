"""
ELT Script: Open Signal Stats — XLSX -> PostgreSQL
Splits data by Technology (3G / 4G) into separate tables.
"""

import os
import pandas as pd
from sqlalchemy import create_engine

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


def extract() -> pd.DataFrame:
    df = pd.read_excel(DATA_PATH)
    df.rename(columns=COLUMN_MAP, inplace=True)
    df["report_end_date"] = pd.to_datetime(df["report_end_date"]).dt.date
    return df


def load_to_postgres(df: pd.DataFrame, table: str, engine) -> None:
    df.to_sql(
        name=table,
        con=engine,
        schema=PG_SCHEMA,
        if_exists="replace",
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
        tech_key = tech.lower().replace(" ", "_")   # e.g. "4g", "3g"
        table    = f"signal_stats_{tech_key}"
        subset   = df[df["technology"] == tech]
        print(f"Loading {tech} data…")
        load_to_postgres(subset, table, engine)

    print("Done.")


if __name__ == "__main__":
    run()