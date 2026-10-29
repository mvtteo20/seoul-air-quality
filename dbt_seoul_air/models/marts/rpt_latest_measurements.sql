with ranked as (
    select
        station_id,
        pollutant_code,
        measurement_value,
        unit,
        measurement_at,
        row_number() over (
            partition by station_id, pollutant_code
            order by measurement_at desc, extraction_id desc
        ) as row_num
    from {{ ref('fct_measurements') }}
),

latest as (
    select * from ranked
    where row_num = 1
)

select
    l.station_id,
    s.station_name,
    l.pollutant_code,
    l.measurement_value,
    l.unit,
    l.measurement_at,
    concat(
        cast(round(s.latitude, 5) as string),
        ',',
        cast(round(s.longitude, 5) as string)
    ) as location,
    l.measurement_at >= timestamp_sub(max(l.measurement_at) over (), interval 24 hour) as is_recent
from latest as l
left join {{ ref('dim_stations') }} as s
    on l.station_id = s.station_id