with ranked as (
    select
        station_id,
        pollutant_code,
        measurement_value,
        unit,
        measurement_at,
        extraction_id,
        row_number() over (
            partition by station_id, pollutant_code, unit, measurement_at
            order by extraction_id
        ) as row_num
    from {{ ref('stg_openaq__measurements') }}
    where pollutant_code in ('co', 'no2', 'o3', 'so2', 'pm10', 'pm25')
        and measurement_value >= 0
        and measurement_value < 9999
)

select
    to_hex(md5(concat(
        cast(station_id as string), '|',
        pollutant_code, '|',
        unit, '|',
        cast(measurement_at as string)
    ))) as measurement_key,
    station_id,
    pollutant_code,
    measurement_value,
    unit,
    measurement_at,
    extraction_id
from ranked
where row_num = 1