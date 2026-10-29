select
    station_id,
    pollutant_code,
    count(*) as n_rows
from {{ ref('rpt_latest_measurements') }}
group by station_id, pollutant_code
having count(*) > 1