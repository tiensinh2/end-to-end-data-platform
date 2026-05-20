from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy, Types
import json

BQ_TABLE = "market-data-platform-496706.binance_data.raw_klines"

def process():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    source = KafkaSource.builder() \
        .set_bootstrap_servers("kafka:9092") \
        .set_topics("binance-klines") \
        .set_group_id("flink-consumer") \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    ds = env.from_source(
        source,
        WatermarkStrategy.no_watermarks(),
        "Kafka Source"
    )

    def insert_to_bq(msg):
        # Khởi tạo client bên trong function
        from google.cloud import bigquery
        bq_client = bigquery.Client()

        record = json.loads(msg)
        print(f"Received: {record['symbol']} | close={record['close']}")

        row = {
            "symbol":     record["symbol"],
            "open_time":  record["open_time"],
            "open":       record["open"],
            "high":       record["high"],
            "low":        record["low"],
            "close":      record["close"],
            "volume":     record["volume"],
            "close_time": record["close_time"],
            "num_trades": record["num_trades"]
        }

        errors = bq_client.insert_rows_json(BQ_TABLE, [row])
        if errors:
            print(f"BQ Error: {errors}")
        else:
            print(f"Inserted: {record['symbol']} | {record['open_time']}")

        return msg

    ds.map(insert_to_bq, output_type=Types.STRING())
    env.execute("Binance Klines Consumer")

if __name__ == "__main__":
    process()