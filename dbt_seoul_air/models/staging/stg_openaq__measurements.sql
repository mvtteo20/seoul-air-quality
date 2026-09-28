SELECT 
    station_id,
    station_name,
    latitude,
    longitude,
    pollutant,
    lower(replace(normalize(pollutant, NFKC), '.', '')) as pollutant_code,
    value as measurement_value,
    unit,
    cast(datetime_utc as timestamp) as measurement_at,
    extraction_id
FROM {{ source('openaq', 'air_quality_measurements') }}