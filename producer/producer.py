import json
import websocket
from kafka import KafkaProducer
from datetime import datetime, timezone

KAFKA_TOPIC = "binance-klines"
KAFKA_BROKER = "localhost:29092"  # dùng port 29092

SYMBOLS = ["btcusdt", "ethusdt", "bnbusdt"]

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def on_message(ws, message):
    data = json.loads(message)

    if "data" not in data:
        return

    kline = data["data"].get("k")
    if not kline:
        return

    if not kline["x"]:
        return

    record = {
        "symbol":     kline["s"],
        "open_time":  datetime.fromtimestamp(kline["t"] / 1000, timezone.utc).isoformat(),
        "open":       float(kline["o"]),
        "high":       float(kline["h"]),
        "low":        float(kline["l"]),
        "close":      float(kline["c"]),
        "volume":     float(kline["v"]),
        "close_time": datetime.fromtimestamp(kline["T"] / 1000, timezone.utc).isoformat(),
        "num_trades": int(kline["n"])
    }

    producer.send(KAFKA_TOPIC, value=record)
    print(f"Sent: {record['symbol']} | close={record['close']} | time={record['open_time']}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, *args):
    print("Connection closed")

def on_open(ws):
    print("Connected to Binance WebSocket")

if __name__ == "__main__":
    streams = "/".join([f"{s}@kline_1m" for s in SYMBOLS])
    url = f"wss://stream.binance.com:9443/stream?streams={streams}"

    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()