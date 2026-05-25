import json
import os
from datetime import datetime
from confluent_kafka import Producer
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC        = "speed_test"

producer_config = {"bootstrap.servers": KAFKA_BROKER}
producer        = Producer(producer_config)
app             = FastAPI()

class SpeedTestResult(BaseModel):
    timestamp: datetime = None
    isp: str
    ip: str
    location: str
    download_speed_mbps: float
    upload_speed_mbps: float
    idle_latency_ms: float
    download_latency_ms: float
    upload_latency_ms: float

def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} : partition {msg.partition()} : offset {msg.offset()}")


@app.post("/v1/speed-test")
def receive_speed_test(result: SpeedTestResult):
    if result.timestamp is None:
        result.timestamp = datetime.utcnow()

    payload = json.dumps(result.model_dump(mode="json")).encode("utf-8")

    producer.produce(
        topic=TOPIC,
        value=payload,
        callback=delivery_report,
    )
    producer.flush()

    return {"status": "published", "topic": TOPIC}

@app.get("/health")
def health():
    return {"status": "ok"}