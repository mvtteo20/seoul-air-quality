FROM apache/airflow:3.3.2

ADD requirements.txt .
RUN pip install --no-cache-dir apache-airflow==${AIRFLOW_VERSION} -r requirements.txt

RUN python -m venv /opt/airflow/dbt_venv \
    && /opt/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-core dbt-bigquery