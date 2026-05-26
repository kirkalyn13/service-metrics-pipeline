import json
import os
from confluent_kafka import Consumer
from sqlalchemy import create_engine, text
import subprocess

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
PG_HOST     = os.getenv("PG_HOST", "host.docker.internal")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_DB       = os.getenv("PG_DB", "service_metrics_db")
PG_USER     = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_SCHEMA   = os.getenv("PG_SCHEMA", "public")
TOPIC        = "speed_test"

consumer_config = {
    "bootstrap.servers": KAFKA_BROKER,
    "group.id":          "speed-test-consumer",
    "auto.offset.reset": "earliest",
}
consumer = Consumer(consumer_config)
engine   = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
)

def run_dbt():
    subprocess.run([
        "dbt", "run",
        "--select", "speed_test.*",
        "--profiles-dir", "/root",
        "--project-dir", "/dbt"
    ], check=True)

def ensure_table():
    with engine.begin() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.raw_speed_test (
                timestamp               TIMESTAMP,
                isp                     TEXT,
                ip                      TEXT,
                location                TEXT,
                download_speed_mbps     DOUBLE PRECISION,
                upload_speed_mbps       DOUBLE PRECISION,
                idle_latency_ms         DOUBLE PRECISION,
                download_latency_ms     DOUBLE PRECISION,
                upload_latency_ms       DOUBLE PRECISION
            )
        """))


def insert(record: dict):
    with engine.begin() as conn:
        conn.execute(text(f"""
            INSERT INTO {PG_SCHEMA}.raw_speed_test
                (timestamp, isp, ip, location, download_speed_mbps, upload_speed_mbps, idle_latency_ms, download_latency_ms, upload_latency_ms)
            VALUES
                (:timestamp, :isp, :ip, :location, :download_speed_mbps, :upload_speed_mbps, :idle_latency_ms, :download_latency_ms, :upload_latency_ms)
        """), record)


def run():
    ensure_table()
    consumer.subscribe([TOPIC])
    print(f"🟢 Consumer running — subscribed to {TOPIC}")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"❌ Error: {msg.error()}")
                continue

            record = json.loads(msg.value().decode("utf-8"))
            insert(record)
            print(f"✅ Inserted speed test from {record['ip']} @ {record['location']}")
            run_dbt()

    except KeyboardInterrupt:
        print("\n🔴 Stopping consumer")
    finally:
        consumer.close()


if __name__ == "__main__":
    run()