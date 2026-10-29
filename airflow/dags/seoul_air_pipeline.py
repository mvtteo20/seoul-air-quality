import datetime

import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="seoul_air_pipeline",
    schedule=CronTriggerTimetable("0 9 * * *", timezone="Asia/Seoul"),
    start_date=pendulum.datetime(2026, 10, 1, tz="Asia/Seoul"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 1,
        "retry_delay": datetime.timedelta(minutes=5),
    },
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