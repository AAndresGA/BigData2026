from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="healthcheck_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["demo", "course"],
) as dag:
    check_data_lake = BashOperator(
        task_id="check_data_lake",
        bash_command="ls -la /opt/airflow/data/lake/raw",
    )

    check_spark_jobs = BashOperator(
        task_id="check_spark_jobs",
        bash_command="ls -la /opt/airflow/spark_jobs",
    )

    check_data_lake >> check_spark_jobs
