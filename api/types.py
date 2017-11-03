from typing import List, Dict, Set, Any
from mypy_extensions import TypedDict

MessageType = TypedDict(
    'Message',
    {
        'conversation': str,
        'id': str,
        'author': str,
        'content': str,
        'timestamp': int,
        'read': bool
    }
)

MsgStoreType = Dict[str, List[MessageType]]

ConversationType = TypedDict(
    'ConversationType',
    {
        'id': str,
        'created_at': int,
        'users': List[str]
    }
)

ConvStoreType = Dict[str, ConversationType]
