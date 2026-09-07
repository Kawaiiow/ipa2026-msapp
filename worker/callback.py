from bson import json_util
from router_client import get_interfaces
from database import save_interface_status


def callback(ch, method, props, body):
    job = json_util.loads(body.decode())
    router_ip = job["ip"]
    router_username = job["username"]
    router_password = job["password"]
    print(f"Received job for router {router_ip}")

    try:
        output = get_interfaces(router_ip, router_username, router_password)
        if output:
            save_interface_status(router_ip, output)
            print(f"Saved interface status for {router_ip} to database")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing router {router_ip}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
