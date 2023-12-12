from datetime import datetime
from enum import Enum


#######################################################
#  State status
#######################################################
class StateStatus(Enum):
    UNKNOWN = 'unknown',
    STARTING = 'starting',
    RUNNING = 'running',
    CRASHED = 'crashed',
    PENDING_CONFIG = 'pending_config'

    # ------------------------------------------------------------------------
    def __str__(self):
        return self.name


#######################################################
#  State
#######################################################
class State:
    status: StateStatus = None
    started_at: datetime = None

    # ------------------------------------------------------------------------
    def __init__(self):
        self.status = StateStatus.UNKNOWN
        self.started_at = datetime.now()
