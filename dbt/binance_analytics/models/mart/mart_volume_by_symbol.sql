{{ config(materialized='table') }}

-- Tile 2: Tổng volume và số giao dịch theo symbol theo giờ
select
    symbol,
    timestamp_trunc(open_time, hour) as hour,
    round(sum(volume), 4) as total_volume,
    sum(num_trades) as total_trades,
    round(avg(close), 2) as avg_close_price,
    round(min(low), 2) as min_price,
    round(max(high), 2) as max_price
from {{ ref('stg_klines') }}
group by symbol, timestamp_trunc(open_time, hour)
order by symbol, hour