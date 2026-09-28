# Packages loader


import requests
from datetime import datetime, timedelta, timezone
import time
import json
import os
from dotenv import load_dotenv

# Extraction of air quality data from OpenAQ API for Seoul, South Korea 


load_dotenv()
API_KEY = os.getenv("OPENAQ_API_KEY")
SEOUL_LAT, SEOUL_LON = 37.5665, 126.9780

response = requests.get(
    "https://api.openaq.org/v3/locations",
    params={"coordinates": f"{SEOUL_LAT},{SEOUL_LON}", "radius": 25000, "limit": 1000},
    headers={"X-API-Key": API_KEY}
)

locations = response.json()


# Active stations filtering based on last seen time (within the last 24 hours)


now = datetime.now(timezone.utc)
cutoff_time = now - timedelta(hours=24)

active_stations = []
for station in locations["results"]:
    last_seen_str = station["datetimeLast"]["utc"]
    last_seen = datetime.fromisoformat(last_seen_str.replace("Z", "+00:00"))
    if last_seen >= cutoff_time:
        active_stations.append(station)

print(len(active_stations), "active stations on", len(locations["results"]))


# Formatting the data into a structured list of records


def get_station_measurements(station):
    """ Get the lastmeasurements of a station and return them as a list of records. one line by pollutants"""
    sensor_lookup = {sensor["id"]: sensor["parameter"] for sensor in station["sensors"]}

    try:
        latest_response = requests.get(
            f"https://api.openaq.org/v3/locations/{station['id']}/latest",
            headers={"X-API-Key": API_KEY}
        )
        latest_response.raise_for_status()
        latest_data = latest_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur pour la station {station['name']} : {e}")
        return []
    
    station_records = []
    for measurement in latest_data["results"]:
        parameter = sensor_lookup[measurement["sensorsId"]]
        station_records.append({
            "station_name": station["name"],
            "station_id": station["id"],
            "latitude": station["coordinates"]["latitude"],
            "longitude": station["coordinates"]["longitude"],
            "pollutant": parameter["displayName"],
            "value": measurement["value"],
            "unit": parameter["units"],
            "datetime_utc": measurement["datetime"]["utc"],
        })

    return station_records

records = []

for station in active_stations:
    records.extend(get_station_measurements(station))
    time.sleep(1.1)
    print(f"{station['name']} treated")

print(len(records))


# Saving the records to a JSON file with a timestamped filename


timestamp = datetime.now().strftime("%Y%m%d_%H%M")
filename = f"air_quality_seoul_{timestamp}.json"

with open(filename, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"{len(records)} records saved to {filename}")