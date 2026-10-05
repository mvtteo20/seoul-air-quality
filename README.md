# Seoul Air Quality ELT Pipeline

A personal data engineering project that collects air quality measurements around Seoul from the OpenAQ API and loads them into BigQuery.

## Architecture

OpenAQ API → Python extraction → raw JSON files → BigQuery (raw layer) → dbt (planned) → Airflow (planned) → dashboard (planned)

## Current status

- [x] Extraction from the OpenAQ API
- [x] Idempotent load into BigQuery
- [x] Transformation with dbt
- [ ] Orchestration with Airflow
- [ ] Dashboard
- [ ] Tests and CI

## Data model

| Model | Type | Description |
|-------|------|-------------|
| `stg_openaq__measurements` | view | Raw table with clean column names, typed timestamps and a normalized `pollutant_code` |
| `dim_stations` | table | One row per station, with its latest known name and coordinates |
| `fct_measurements` | table | One row per distinct measurement, deduplicated across extractions |

## Design decisions

- Some stations stopped reporting years ago but the API still returns their last value. Only stations active in the last 24 hours are kept.
- The free OpenAQ tier allows 60 requests per minute, so calls are spaced by 1.1 seconds.
- Each run writes a timestamped file, so a load can be replayed without calling the API again.
- Every record carries an 'extraction_id' (the source file name). A file already present in BigQuery is not loaded twice.
- API keys and credential paths are read from a '.env' file that is never committed.
- Stations are identified by `station_id`, never by name. Two distinct stations can share the same name.
- Consecutive extractions can return the same measurement when a station has not published anything new, so the fact table keeps one row per station, pollutant, unit and timestamp.
- Only the six standard pollutants are kept in the fact table (CO, NO2, O3, SO2, PM10, PM2.5). Isolated sensors such as temperature or humidity are excluded.

## Setup

```
git clone https://github.com/mvtteo20/seoul-air-quality.git
cd seoul-air-quality
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Fill in '.env' with your own OpenAQ API key and the path to your GCP service account key.

You also need a GCP project with a BigQuery dataset named 'seoul_air_quality_raw'.

## Usage

```
python seoul-air-quality.py
python load_to_bigquery.py
```

The first script extracts the latest measurements into a JSON file, the second loads the most recent file into BigQuery.