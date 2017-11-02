from functools import wraps
from typing import Callable
import jwt
from sanic.response import json
from .schemas import ChatMessage


def login_required(handler: Callable):
    @wraps(handler)
    async def decorated(request, *args):
        jwt_auth = request.headers.get('Authorization')
        try:
            auth_info = jwt.decode(jwt_auth)
        except:  # TODO: specify exceptions
            err = {'error': 'You are not authorized'}
            return json(err, 401)
        response = await handler(request, auth_info, *args)
        return response


def store_msg(msg: ChatMessage) -> None:
    pass
