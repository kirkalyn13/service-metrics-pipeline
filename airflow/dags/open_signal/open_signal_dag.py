"""
Airflow DAG: open_signal_pipeline
Orchestrates: XLSX extract/load -> dbt transform
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import sys, os

sys.path.insert(0, '/opt/airflow')
sys.path.insert(0, "/opt/elt/open_signal")

from elt.open_signal.extract_load import run as _run_elt

default_args = {
    "owner":            "engineering",
    "retries":          2,
    "retry_delay":      timedelta(minutes=1),
    "email_on_failure": False,
}

DAG_ID   = "open_signal_pipeline"
SCHEDULE = "@daily"
DBT_DIR  = "/opt/dbt"


def ensure_schema(**_):
    """Create the raw schema and tables if they don't exist."""
    hook = PostgresHook(postgres_conn_id="open_signal_postgres")
    ddl = """
        CREATE TABLE IF NOT EXISTS signal_stats_4g (
            aggregation                  INTEGER,
            report_end_date              DATE,
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
        );

        CREATE TABLE IF NOT EXISTS signal_stats_3g
            (LIKE signal_stats_4g INCLUDING ALL);
    """
    hook.run(ddl)
    print("Schema & tables ready.")


with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="NL Open Signal: XLSX -> Postgres -> dbt",
    schedule_interval=SCHEDULE,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["open signal", "elt", "dbt", "metrics"],
) as dag:

    t_schema = PythonOperator(
        task_id="ensure_schema",
        python_callable=ensure_schema,
    )

    t_extract_load = PythonOperator(
        task_id="extract_load_xlsx",
        python_callable=_run_elt,
    )

    t_dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run --profiles-dir /home/airflow/.dbt --target dev",
    )

    t_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --profiles-dir /home/airflow/.dbt --target dev",
    )

    t_schema >> t_extract_load >> t_dbt_run >> t_dbt_test