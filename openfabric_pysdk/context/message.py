from datetime import datetime
from enum import Enum


#######################################################
#  Message type
#######################################################
class MessageType(Enum):
    INFO = 'info',
    ERROR = 'error',
    WARNING = 'warning'

    # ------------------------------------------------------------------------
    def __str__(self):
        return self.name


#######################################################
#  Message
#######################################################
class Message:
    type: MessageType = 0
    content: str = None
    created_at: datetime = None

    def __init__(self):
        self.created_at = datetime.now()

    # ------------------------------------------------------------------------
    def __eq__(self, other):
        if not isinstance(other, Message):
            return NotImplemented
        return self.type == other.type and self.content == other.content

    # ------------------------------------------------------------------------
    def __key(self):
        return self.type, self.content

    # ------------------------------------------------------------------------
    def __hash__(self):
        return hash(self.__key())
