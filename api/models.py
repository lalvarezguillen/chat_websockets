import uuid
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
    
