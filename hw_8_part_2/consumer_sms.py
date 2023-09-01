import pika

import time
import json

from models import Contacts
from bson.objectid import ObjectId

from mongo_connection import connect

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='phone', durable=True)
print(' [*] Waiting for data to notify clients with email. To exit press CTRL+C')


def callback(ch, method, properties, body):
    message = json.loads(body.decode())
    contact = Contacts.objects.get(id=message['contact_id'])
    print(f" [x] Received {message['value']}")
    time.sleep(1)
    contact.update(set__processed=True)
    print(f" [x] Done: {method.delivery_tag}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='phone', on_message_callback=callback)

if __name__ == '__main__':
    channel.start_consuming()

