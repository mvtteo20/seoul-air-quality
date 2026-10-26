import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="seoul_air_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    catchup=False,
    tags=["seoul-air-quality"],
) as dag:
    extract = BashOperator(
        task_id="extract_openaq",
        bash_command="cd /opt/airflow/data && python /opt/airflow/project/seoul-air-quality.py",
    )

    load = BashOperator(
        task_id="load_to_bigquery",
        bash_command="cd /opt/airflow/data && python /opt/airflow/project/load_to_bigquery.py",
    )

    transform = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "cd /opt/airflow/project/dbt_seoul_air && "
            "/opt/airflow/dbt_venv/bin/dbt build --no-partial-parse"
        ),
    )

    extract >> load >> transform