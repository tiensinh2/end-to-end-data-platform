{{ config(materialized='table') }}

-- Tile 1: Giá đóng cửa theo thời gian cho từng symbol
select
    symbol,
    open_time,
    open,
    high,
    low,
    close,
    volume,
    num_trades,
    -- tính price change %
    round(
        (close - lag(close) over (
            partition by symbol
            order by open_time
        )) / lag(close) over (
            partition by symbol
            order by open_time
        ) * 100,
    2) as price_change_pct
from {{ ref('stg_klines') }}
order by symbol, open_time