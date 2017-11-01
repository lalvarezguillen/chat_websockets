from sanic import Sanic
from sanic.exceptions import abort
from sanic.response import json
from passlib.hash import pbkdf2_sha256
import jwt

from .models import User
from .schemas import IdEmail, EmailPass


APP = Sanic(__name__)
APP.config.SECRET = 'some secret'


DUMMY_SUMMARY = {
    'user_id': 'barack-obama',
    'chats':[
        {
            'chat_id': 'barack-trump',
            'last_messages': [
                {
                    'message_id': 'message1',
                    'author': 'barack-obama',
                    'content': 'Your not too bright',
                    'timestamp': 1509388065.295844,
                    'read': True
                },
                {
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
    return json(DUMMY_SUMMARY)


@APP.route('/user', methods=['PUT'])
async def register_user(request):
    '''
    Try to create a user and return a JWT token for him/her
    '''
    # TODO: Use a serializer like the one on flask-restful
    req_data, sch_err = EmailPass().load(request.data)
    if sch_err:
        return json({'error': sch_err}, status=400)
    email = req_data.lower()
    if User.objects.raw({'email': email}).count():
        err = {
            'error': f'The address "{email}" is already registered'
        }
        return json(err, status=400)
    pwd = pbkdf2_sha256.hash(request.data.password)
    user = User(email=email, password=pwd)
    user.save()
    token = jwt.encode({'user_id': user.id},
                       APP.config.SECRET,
                       algorithm='HS256')
    return json({'jwt_auth': token})


@APP.route('/auth_token', methods=['PUT'])
async def create_auth_token(request):
    '''
    Authenticate a user and return a JWT for him/her.
    '''
    req_data, sch_err = EmailPass().load(request.data)
    if sch_err:
        return json({'error': sch_err}, status=400)
    email = req_data.email.lower()
    try:
        user = User.objects.get({'email': email})
    except User.DoesNotExist:
        err = {
            'error': f'Wrong email: {email}'
        }
        return json(err, status=401)
    if pbkdf2_sha256.verify(req_data.password, user.password_crypto):
        token = jwt.encode({'user_id': user.id},
                           APP.config.SECRET,
                           algorithm='HS256')
        return json({'jwt_auth': token})
    else:
        err = {'error': 'The password is not right'}
        return json(err, status=401)


@APP.route('/chat_room', methods=['PUT'])
async def create_chat_room(request):
    pass


@APP.websocket('/ws')
async def ws_test(request, ws):
    print(ws.clients)
    while True:
        await ws.send('What is your name?')
        name = await ws.recv()
        print(f'name is {name}')


if __name__ == '__main__':
    APP.run(debug=True)
