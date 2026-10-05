select
    measurement_key,
    station_id,
    pollutant_code,
    measurement_value
from {{ ref('fct_measurements') }}
where measurement_value >= 9999
   or measurement_value < 0