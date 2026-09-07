import pika
import pika.credentials
import os

rabbitmq_user = os.environ.get("RABBITMQ_DEFAULT_USER")
rabbitmq_pass = os.environ.get("RABBITMQ_DEFAULT_PASS")

def produce(host, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)))
    channel = connection.channel()

    channel.exchange_declare(exchange="jobs", exchange_type="direct")
    channel.queue_declare(queue="router_jobs", durable=True)
    channel.queue_bind(queue="router_jobs", exchange="jobs", routing_key="check_interfaces")

    channel.basic_publish(exchange="jobs", routing_key="check_interfaces", body=body)

    connection.close()

if __name__ == "__main__":
    produce("rabbitmq", "192.168.1.44")
