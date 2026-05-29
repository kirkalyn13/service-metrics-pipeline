"""
ELT Script: High Utilization Data — CSV -> PostgreSQL
Raw tables are partitioned by year on rdata.
"""

import os
import sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import ensure_partitioned_table, load_to_postgres

DATA_PATH   = os.getenv("HIGH_UTILIZATION_DATA_PATH", "/data/high_utilization")

COLUMN_MAP = {
    "WK":                              "week",
    "DATE":                            "date",
    "TECH":                            "tech",
    "VENDOR":                          "vendor",
    "SITE_NO":                         "site_no",
    "SITE_NAME":                       "site_name",
    "BTS_NAME":                        "bts_name",
    "CELL_NAME":                       "cell_name",
    "MUNICIPALITY":                    "municipality",
    "PROVINCE":                        "province",
    "AREA":                            "area",
    "BAND":                            "band",
    "PRB_UTILIZATION":                 "prb_utilization",
    "RRC_USER":                        "rrc_user",
    "PAYLOAD":                         "payload",
    "LTE_DL_USER_THROUGHPUT_kbps":     "dl_user_throughput_kbps",
    "LTE_UL_USER_THROUGHPUT_kbps":     "ul_user_throughput_kbps",
    "SITE STATUS":                     "site_status",
}

TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {schema}.{table} (
        week                         INTEGER,
        date                         DATE NOT NULL,
        tech                         TEXT,
        vendor                       TEXT,
        site_no                      TEXT,
        site_name                    TEXT,
        bts_name                     TEXT,
        cell_name                    TEXT,
        municipality                 TEXT,
        province                     TEXT,
        area                         TEXT,
        band                         TEXT,
        prb_utilization              DOUBLE PRECISION,
        rrc_user                     DOUBLE PRECISION,
        payload                      DOUBLE PRECISION,
        dl_user_throughput_kbps      DOUBLE PRECISION,
        ul_user_throughput_kbps      DOUBLE PRECISION,
        site_status                  TEXT
    ) PARTITION BY RANGE (date);
"""

PARTITION_DDL = """
    CREATE TABLE IF NOT EXISTS {schema}.{table}_y{year}
    PARTITION OF {schema}.{table}
    FOR VALUES FROM ('01/01/{year}') TO ('01/01/{next_year}');
"""


def extract() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="latin-1")
    df.rename(columns=COLUMN_MAP, inplace=True)
    df = df[[col for col in COLUMN_MAP.values() if col in df.columns]]
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

def run():
    print("Extracting from XLSX…")
    df = extract()

    table    = f"raw_high_utilization"
    years    = sorted(df["date"].apply(lambda d: d.year).unique().tolist())

    print(f"Ensuring partitioned table…")
    ensure_partitioned_table(table, TABLE_DDL, PARTITION_DDL, years)

    print(f"Loading high utilization data…")
    load_to_postgres(df, table)
        
    print("Done.")


if __name__ == "__main__":
    run()