{{ config(materialized='view') }}

with source as (
    select
        symbol,
        timestamp(open_time) as open_time,
        timestamp(close_time) as close_time,
        cast(open as float64) as open,
        cast(high as float64) as high,
        cast(low as float64) as low,
        cast(close as float64) as close,
        cast(volume as float64) as volume,
        cast(num_trades as int64) as num_trades
    from {{ source('binance', 'raw_klines') }}
    where open_time is not null
        and symbol is not null
)

select * from source