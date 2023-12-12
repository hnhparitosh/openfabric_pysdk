import logging
import os
import queue
from enum import Enum
from typing import List, Any

from openfabric_pysdk.store import Store

STATE = 'state'


#######################################################
#  TaskType
#######################################################
class TaskType(Enum):
    QUEUED = 'queued',
    REQUESTED = 'requested',
    COMPLETED = 'completed',

    def __str__(self):
        return self.name


#######################################################
#  Task
#######################################################
class Task:
    __tasks: queue.Queue = None
    __store: Store = None

    # ------------------------------------------------------------------------
    def __init__(self):
        self.__tasks = queue.Queue()
        self.__store = Store(path=f"{os.getcwd()}/datastore", autodump=True)
        pending_tasks = self.__load(TaskType.QUEUED)
        if pending_tasks:
            logging.info(f"Openfabric - restore pre-existing tasks: {pending_tasks}")
            [self.__tasks.put(sid) for sid in pending_tasks]

    # ------------------------------------------------------------------------
    def __del__(self):
        self.__tasks = queue.Queue()

    # ------------------------------------------------------------------------
    def empty(self) -> bool:
        return self.__tasks.empty()

    # ------------------------------------------------------------------------
    def next(self) -> str:
        tid = self.__tasks.get(False)
        self.__save(TaskType.QUEUED, list(self.__tasks.queue))
        self.__append(TaskType.COMPLETED, tid)
        return tid

    # ------------------------------------------------------------------------
    def add(self, tid: str):
        self.__tasks.put(tid)
        self.__save(TaskType.QUEUED, list(self.__tasks.queue))
        self.__append(TaskType.REQUESTED, tid)

    # ------------------------------------------------------------------------
    def rem(self, tid: str):
        self.__remove(TaskType.REQUESTED, tid)
        self.__remove(TaskType.COMPLETED, tid)

    # ------------------------------------------------------------------------
    def all(self):
        return list(
            set(
                self.__load(TaskType.COMPLETED, list()) +
                self.__load(TaskType.REQUESTED, list()) +
                self.__load(TaskType.QUEUED, list())
            )
        )

    # ------------------------------------------------------------------------
    def __append(self, task_type: TaskType, tid: str):
        entries: List[str] = self.__load(task_type, list())
        entries.append(tid)
        self.__save(task_type, entries)

    def __remove(self, task_type: TaskType, tid: str):
        entries: List[str] = self.__load(task_type, list())
        if tid in entries:
            entries.remove(tid)
        self.__save(task_type, entries)

    def __save(self, task_type: TaskType, value: Any):
        self.__store.set(STATE, str(task_type), value)

    def __load(self, task_type: TaskType, default=None):
        return self.__store.get(STATE, str(task_type), default)
