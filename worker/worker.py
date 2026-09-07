import json
from datetime import datetime, timezone
import pika
import os
from netmiko import ConnectHandler
from pymongo import MongoClient

# ================= Configuration =================
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_USER = os.environ.get("RABBITMQ_DEFAULT_USER")
RABBITMQ_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS")
QUEUE_NAME = "router_jobs"

MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = "interface_status"

# ================= MongoDB Setup =================
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]


def process_router_job(job_data: dict) -> dict:
    """SSH เข้าไปยัง Router และรันคำสั่งพร้อมแปลงข้อมูลด้วย TextFSM"""
    device_params = {
        "device_type": job_data.get("device_type", "cisco_ios"),
        "host": job_data["ip"],
        "username": job_data["username"],
        "password": job_data["password"],
        "secret": job_data.get("secret", job_data["password"]),
        "timeout": 15,
    }

    print(f"[*] Connecting to {device_params['host']} via SSH...")

    with ConnectHandler(**device_params) as net_connect:
        net_connect.enable()
        # use_textfsm=True จะแปลง output ให้อยู่ในรูป List[dict]
        parsed_output = net_connect.send_command(
            "show ip interface brief", use_textfsm=True
        )

    return {
        "router_ip": device_params["host"],
        "interfaces": parsed_output,
        "timestamp": datetime.now(timezone.utc),
    }


def callback(ch, method, properties, body):
    """ฟังก์ชัน Callback เมื่อมี Message เข้ามาใน Queue"""
    try:
        payload = json.loads(body.decode("utf-8"))
        print(f"\n[+] Received job for router: {payload.get('ip')}")

        # 1. SSH + Parse TextFSM
        result = process_router_job(payload)

        # 2. บันทึกลง MongoDB
        collection.insert_one(result)

        # ยืนยันการทำงานสำเร็จ (Ack message ออกจาก Queue)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as err:
        print(f"[!] Error processing task: {err}")
        # กรณี Error: ปฏิเสธ message (requeue=False เพื่อป้องกัน infinite loop)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_worker():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=5672,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # ประกาศคิวและตั้ง prefetch_count เพื่อรับทีละ 1 งาน
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[*] Worker1 is running. Waiting for messages in '{QUEUE_NAME}'...")
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()
