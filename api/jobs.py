'''
Async jobs for this project
'''
from celery import Celery
from .types import MessageType
from .models import Message


CELERY_SINGLETON = Celery(__name__,
                          broker='redis://localhost:6379',
                          backend='redis://localhost:6379')


@CELERY_SINGLETON.task
def save_msg_in_db(msg: MessageType) -> None:
    msg_entry = Message(**msg)
    msg_entry.save()
