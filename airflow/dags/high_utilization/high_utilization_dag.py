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

DAG_ID   = "high_utilization_pipeline"
SCHEDULE = "@daily"
DBT_DIR  = "/opt/dbt"


def ensure_schema(**_):
    """Create the raw schema and tables if they don't exist."""
    hook = PostgresHook(postgres_conn_id="open_signal_postgres")
    ddl = """
        CREATE TABLE IF NOT EXISTS mart_high_utilization_nl (
            week                         INTEGER,
            date                         DATE NOT NULL,
            tech                         TEXT,
            vendor                       TEXT,
            site_name                    TEXT,
            cell_name                    TEXT,
            municipality                 TEXT,
            province                     TEXT,
            band                         TEXT,
            prb_utilization              DOUBLE PRECISION,
            rrc_user                     DOUBLE PRECISION,
            payload                      DOUBLE PRECISION,
            dl_user_throughput_kbps      DOUBLE PRECISION,
            site_status                  TEXT,
            is_high_util                 BOOLEAN
        );
    """
    hook.run(ddl)
    print("Schema & tables ready.")


with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="NL High Utilization: CSV -> Postgres -> dbt",
    schedule_interval=SCHEDULE,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["high utiization", "elt", "dbt", "metrics"],
) as dag:

    t_schema = PythonOperator(
        task_id="ensure_schema",
        python_callable=ensure_schema,
    )

    t_extract_load = PythonOperator(
        task_id="extract_load_csv",
        python_callable=_run_elt,
    )

    t_dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run --select high_utilization.* --profiles-dir /home/airflow/.dbt --target dev",
    )

    t_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --select high_utilization.* --profiles-dir /home/airflow/.dbt --target dev",
    )

    t_schema >> t_extract_load >> t_dbt_run >> t_dbt_test