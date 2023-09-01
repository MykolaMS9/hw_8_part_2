import random
from datetime import datetime
import json

import pika
from faker import Faker

from models import Contacts, Notify
from mongo_connection import connect

fake = Faker('uk-UA')

# docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='task_send', exchange_type='direct')
channel.queue_declare(queue='phone', durable=True)
channel.queue_declare(queue='email', durable=True)
channel.queue_bind(exchange='task_send', queue='phone')
channel.queue_bind(exchange='task_send', queue='email')


def create_contacts(n=20):
    for _ in range(n):
        contact = Contacts(
            fullname=f"{fake.first_name()} {fake.last_name()}",
            email=fake.email(),
            phone=fake.phone_number(),
            notify_way=random.choice([Notify.EMAIL, Notify.PHONE])
        ).save()


def create_message_queue():
    contacts = Contacts.objects()
    i = 1
    for contact in contacts:
        contact_value = contact.to_mongo().to_dict()
        message = {
            "id": i,
            "contact_id": str(contact_value['_id']),
            "value": f"Dear {contact_value['fullname']}! Congratulation! We have a lot of new information about new products in shops. We are waiting for you.",
            "date": datetime.now().isoformat()
        }
        i += 1
        channel.basic_publish(
            exchange='task_send',
            routing_key=contact_value['notify_way'],
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(" [x] Sent %r" % message)
        contact.update(set__processed=False)
    connection.close()


if __name__ == '__main__':
    # create_contacts()
    create_message_queue()
