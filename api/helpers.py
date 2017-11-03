from functools import wraps
from typing import Callable
import jwt
from sanic.response import json
from .models import Conversation
from .schemas import ChatMessage, ConvSchema
from .types import (MsgStoreType,
                    MessageType,
                    ConversationType,
                    ConvStoreType)
from .jobs import save_msg_in_db


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


def store_msg(msg: MessageType, msg_store: MsgStoreType) -> None:
    msg_store[msg['conversation']].append(msg)
    save_msg_in_db(msg)


def get_conversation(
        conv_id: str,
        conversations: ConvStoreType
    ) -> ConversationType:
    if conv_id not in conversations:
        conv_obj = Conversation.objects.get({'_id': conv_id})
        conv = ConvSchema().dump(conv_obj)
        conversations[conv_id] = conv
    else:
        conv = conversations[conv_id]
    return conv
