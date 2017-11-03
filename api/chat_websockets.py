import json
from typing import Set, Dict, Any, List

from sanic import Sanic
from sanic.exceptions import abort
from sanic.response import json as jsonr
from passlib.hash import pbkdf2_sha256
import jwt

from .models import User, Conversation, Message
from .schemas import (IdEmail,
                      EmailPass,
                      UserId,
                      Interlocutor,
                      ConversationSchema,
                      ChatMessage)
from .helpers import (login_required,
                      store_msg,
                      get_conversation)
from .types import (MessageType,
                    MsgStoreType,
                    ConvStoreType)


APP = Sanic(__name__)
APP.config.SECRET = 'some secret'


DUMMY_SUMMARY = {
    'user_id': 'barack-obama',
    'chats':[
        {
            'chat_id': 'barack-trump',
            'last_messages': [
                {
                    'chat_id': 'barack-trump',
                    'message_id': 'message1',
                    'author': 'barack-obama',
                    'content': 'Your not too bright',
                    'timestamp': 1509388065.295844,
                    'read': True
                },
                {
                    'chat_id': 'barack-trump',
                    'message_id': 'message2',
                    'author': 'donald-trump',
                    'content': 'Fake news!',
                    'timestamp': 1509388085.295844,
                    'read': True
                }
            ]
        }
    ]
}

@APP.route('/')
async def get_chat_summary(request):
    print(request)
    return jsonr(DUMMY_SUMMARY)


@APP.route('/user', methods=['PUT'])
async def register_user(request):
    '''
    Try to create a user and return a JWT token for him/her
    '''
    req_data, sch_err = EmailPass().load(request.data)
    if sch_err:
        return jsonr({'error': sch_err}, 400)
    email = req_data.lower()
    if User.objects.raw({'email': email}).count():
        err = {
            'error': f'The address "{email}" is already registered'
        }
        return jsonr(err, 400)
    pwd = pbkdf2_sha256.hash(request.data.password)
    user = User(email=email, password=pwd)
    user.save()
    token = jwt.encode({'user_id': user.id},
                       APP.config.SECRET,
                       algorithm='HS256')
    return jsonr({'jwt_auth': token})


@APP.route('/auth_token', methods=['PUT'])
async def create_auth_token(request):
    '''
    Authenticate a user and return a JWT for him/her.
    '''
    req_data, sch_err = EmailPass().load(request.data)
    if sch_err:
        return jsonr({'error': sch_err}, 400)
    email = req_data.email.lower()
    try:
        user = User.objects.get({'email': email})
    except User.DoesNotExist:
        err = {
            'error': f'Wrong email: {email}'
        }
        return jsonr(err, status=401)
    if pbkdf2_sha256.verify(req_data.password, user.password_crypto):
        token = jwt.encode({'user_id': user.id},
                           APP.config.SECRET,
                           algorithm='HS256')
        return jsonr({'jwt_auth': token})
    else:
        err = {'error': 'The password is not right'}
        return jsonr(err, 401)


@APP.route('/chat_room', methods=['PUT'])
@login_required
async def create_chat_room(request, auth_info):
    # The user will send his interlocutor's ID
    req_data, sch_err = Interlocutor().load(request.data)
    interlocutor = req_data.id
    if sch_err:
        return jsonr({'error': sch_err}, 400)
    users = [auth_info['user_id'], interlocutor]
    users.sort()
    try:
        conv = Conversation.objects.get({'users': users})
    except Conversation.DoesNotExist:
        conv = Conversation(users=users)
        conv.save()
    serialized_conv = ConversationSchema().dump(conv)
    return jsonr(serialized_conv)


# TODO: Instead of Any it should be type Websocket
CLIENTS: Dict[str, Any] = {}
# TODO: Instead of Any it should be ConversationType
CONVERSATIONS: ConvStoreType = {}
MSG_STORE: MsgStoreType = {}

@APP.websocket('/ws')
@login_required
async def ws_test(request, auth_info, wsock):
    CLIENTS[auth_info['user_id']] = wsock
    while True:
        raw_msg = await wsock.recv()
        msg, sch_err = ChatMessage().load(json.loads(raw_msg))
        if not sch_err:
            store_msg(ChatMessage().dump(msg), MSG_STORE)
            try:
                conv = get_conversation(
                    msg['conversation'],
                    CONVERSATIONS
                )
            except Conversation.DoesNotExist:
                continue
            interlocutor_id = next(user for user in conv['users']
                                   if user != msg['author'])
            if interlocutor_id in CLIENTS:
                interlocutor = CLIENTS[interlocutor_id]
                if interlocutor.status == 'OPEN':
                    await interlocutor.send(msg)


if __name__ == '__main__':
    APP.run(debug=True)
