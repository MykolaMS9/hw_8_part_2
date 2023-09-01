from enum import Enum
from mongoengine import Document
from mongoengine.fields import StringField, BooleanField, EnumField


class Notify(Enum):
    EMAIL = 'email'
    PHONE = 'phone'


class Contacts(Document):
    fullname = StringField(required=True)
    email = StringField(max_length=100, required=True)
    phone = StringField(required=True)
    notify_way = EnumField(Notify, required=True)
    processed = BooleanField(required=True, default=False)
