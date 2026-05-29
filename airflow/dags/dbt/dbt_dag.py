"""
DAG: dbt_pipeline
Runs all dbt models on a schedule.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner":            "engineering",
    "retries":          2,
    "retry_delay":      timedelta(minutes=1),
    "email_on_failure": False,
}

DBT_DIR      = "/opt/dbt"
PROFILES_DIR = "/home/airflow/.dbt"
SCHEDULE = "*/15 * * * *"

with DAG(
    dag_id="dbt_pipeline",
    default_args=default_args,
    description="Runs all dbt models on a schedule",
    schedule_interval=SCHEDULE,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["dbt"],
) as dag:

    t_dbt_run_open_signal = BashOperator(
        task_id="dbt_run_open_signal",
        bash_command=f"cd {DBT_DIR} && dbt run --select open_signal.* --profiles-dir {PROFILES_DIR} --project-dir {DBT_DIR}",
    )

    t_dbt_run_speed_test = BashOperator(
        task_id="dbt_run_speed_test",
        bash_command=f"cd {DBT_DIR} && dbt run --select speed_test.* --profiles-dir {PROFILES_DIR} --project-dir {DBT_DIR}",
    )

    t_dbt_run_high_utilization = BashOperator(
        task_id="dbt_run_high_utilization",
        bash_command=f"cd {DBT_DIR} && dbt run --select high_utilization.* --profiles-dir {PROFILES_DIR} --project-dir {DBT_DIR}",
    )

    t_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --profiles-dir {PROFILES_DIR} --project-dir {DBT_DIR}",
    )

    [t_dbt_run_open_signal, t_dbt_run_speed_test, t_dbt_run_high_utilization] >> t_dbt_test