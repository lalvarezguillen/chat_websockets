import uuid
import datetime
import pymongo
from pymongo.operations import IndexModel
from pymodm import connect
from pymodm import MongoModel, fields


MONGO_CONN_ALIAS = 'websockets_test'
connect('mongodb://localhost:27017/websockts_test',
        alias=MONGO_CONN_ALIAS)


class User(MongoModel):
    id = fields.CharField(
        primary_key=True,
        default=lambda: str(uuid.uuid1())
    )
    email = fields.EmailField()
    password_crypto = fields.CharField()
    class Meta:
        connection_alias = MONGO_CONN_ALIAS
        indexes = [
            IndexModel([('email', pymongo.DESCENDING)])
        ]


class Conversation(MongoModel):
    '''
    One on one chat
    '''
    id = fields.CharField(
        primary_key=True,
        default=lambda: str(uuid.uuid1())
    )
    created_at = fields.IntegerField()
    users = fields.ListField(field=fields.ReferenceField(User))
    class Meta:
        connection_alias = MONGO_CONN_ALIAS
        indexes = [
            IndexModel([('users', pymongo.DESCENDING)])
        ]


class Message(MongoModel):
    id = fields.CharField(
        primary_key=True,
        default=lambda: str(uuid.uuid1())
    )
    author = fields.ReferenceField(User)
    conversation = fields.ReferenceField(Conversation)
    timestamp = fields.DateTimeField(default=datetime.datetime.utcnow)
    content = fields.CharField()
    class Meta:
        connection_alias = MONGO_CONN_ALIAS
        indexes = [
            IndexModel([('author', pymongo.DESCENDING)]),
            IndexModel([('conversation', pymongo.DESCENDING)]),
            IndexModel([('timestamp', pymongo.DESCENDING)])
        ]
