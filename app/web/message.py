"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from enum import Enum
from pydantic import BaseModel
from fastapi import Request


class MessageCategory(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Message(BaseModel):
    category: MessageCategory = MessageCategory.INFO
    message: str


class MessageBroker(object):

    _instance = None

    @staticmethod
    def instance() -> "MessageBroker":
        if MessageBroker._instance:
            return MessageBroker._instance
        else:
            return MessageBroker()

    def __init__(self):
        if not MessageBroker._instance:
            MessageBroker._instance = self
        else:
            return

        # key is session id (str)
        self.queue: dict[str, list[Message]] = {}

    @staticmethod
    def push(request: Request, message: Message):
        """
        adds a new message to the queue
        """
        sessid = request.cookies.get("session", None)
        if sessid is None:
            return

        self = MessageBroker.instance()
        current = self.queue.get(sessid, [])
        current.append(message)
        self.queue.update({sessid: current})

    @staticmethod
    def pull(request: Request) -> Message | None:
        """
        returns and removes the newest message from the queue
        """
        sessid = request.cookies.get("session", None)
        if sessid is None:
            return

        self = MessageBroker.instance()
        current = self.queue.get(sessid, [])
        response = current.pop() if len(current) > 0 else None
        self.queue.update({sessid: current})
        return response

    @staticmethod
    def all(request: Request) -> list[Message]:
        """
        returns and removes the whole queue
        """
        sessid = request.cookies.get("session", None)
        if sessid is None:
            return []

        response = MessageBroker.instance().queue.pop(sessid, [])
        return response
