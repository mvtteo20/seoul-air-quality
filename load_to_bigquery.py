from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound
from dotenv import load_dotenv
import json
import glob
import os


load_dotenv()

credentials = service_account.Credentials.from_service_account_file(
    os.getenv("GCP_KEY_PATH")
)
client = bigquery.Client(credentials=credentials, project= credentials.project_id)

extraction_files = glob.glob("air_quality_seoul_*.json")
latest_file = max(extraction_files, key=os.path.getctime)

print(f"File Loading {latest_file}")

with open(latest_file, "r", encoding="utf-8") as f:
    records = json.load(f)

extraction_id = os.path.basename(latest_file)

for record in records:
    record["extraction_id"] = extraction_id

TABLE_ID = f"{client.project}.seoul_air_quality_raw.air_quality_measurements"

already_loaded = False
try:
    check_query = f"""
        SELECT COUNT(*) AS count
        FROM `{TABLE_ID}`
        WHERE extraction_id = @extraction_id
    """
    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("extraction_id", "STRING", extraction_id)
        ]
    )
    result = client.query(check_query, job_config=query_config).result()
    row = next(iter(result))
    already_loaded = row.count > 0
except NotFound:
    already_loaded = False

if already_loaded:
    print(f"{extraction_id} has already been loaded, doing nothing.")
else:
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition="WRITE_APPEND",
    )
    load_job = client.load_table_from_json(records, TABLE_ID, job_config=job_config)
    load_job.result()
    print(f"{load_job.output_rows} rows loaded into {TABLE_ID}")