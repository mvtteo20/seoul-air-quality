with ranked as (
    select
        station_id,
        station_name,
        latitude,
        longitude,
        row_number() over (
            partition by station_id
            order by measurement_at desc, extraction_id desc
        ) as row_num
    from {{ ref('stg_openaq__measurements') }}
)

select
    station_id,
    station_name,
    latitude,
    longitude
from ranked
where row_num = 1