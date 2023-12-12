import os
import logging
import threading
import traceback
import uuid
from time import sleep
from typing import Any, Dict, List

import traceback

from openfabric_pysdk.benchmark import MeasureBlockTime
from openfabric_pysdk.context import Ray, RaySchema, RayStatus
from openfabric_pysdk.loader import InputSchema, OutputSchema
from openfabric_pysdk.task import Task
from openfabric_pysdk.app import App
from openfabric_pysdk.store import Store


#######################################################
#  Engine
#######################################################
class Engine:
    __app: App = None
    __store: Store = None
    __rays: Dict[str, Ray] = None
    __task: Task = None
    __instances: int = 0
    __running: bool = False
    __current_qid: str = None
    __worker: threading.Thread = None
    __lock: threading.Condition = threading.Condition()

    # ------------------------------------------------------------------------
    def __init__(self):
        self.__rays = dict()
        self.__store = Store(path=f"{os.getcwd()}/datastore")
        self.__lock.acquire()
        if self.__instances == 0:
            self.__task = Task()

            # Populate rays on startup
            for qid in self.__task.all():
                ray = self.read(qid, 'ray', RaySchema().load)
                if ray is None:
                    continue
                self.__rays[qid] = ray

            self.__worker = threading.Thread(target=self.__process, args=())
            self.__worker.start()

        self.__instances = self.__instances + 1
        self.__lock.release()

        # Wait for processing thread to start
        while not self.__running:
            sleep(0.1)

    # ------------------------------------------------------------------------
    def __del__(self):
        self.__lock.acquire()
        if self.__instances > 0:
            self.__lock.release()
            return

        self.__running = False

        self.__lock.notify_all()
        self.__lock.release()

    # ------------------------------------------------------------------------
    def __process(self):
        self.__running = True
        while self.__running:
            self.__lock.acquire()
            self.__current_qid = None
            while self.__running and self.__task.empty():
                self.__lock.wait()
            try:
                self.__current_qid = self.__task.next()
            except:
                logging.warning("Openfabric - queue empty!")
                traceback.print_exc()
            finally:
                self.__lock.release()

            if self.__running and self.__current_qid is not None:
                self.process(self.__current_qid)

    # ------------------------------------------------------------------------
    def prepare(self, app: App, data: str, qid=None, sid=None, uid=None, rid=None) -> str:
        self.__lock.acquire()
        if qid is None:
            qid: str = uuid.uuid4().hex
        ray = self.ray(qid)
        ray.status = RayStatus.QUEUED
        ray.sid = sid
        ray.uid = uid
        ray.rid = rid
        self.write(qid, 'ray', ray, RaySchema().dump)
        self.write(qid, 'in', data)
        # Make sure the worker is able to read the input and state.
        self.flush(qid)
        self.__app = app
        self.__task.add(qid)
        self.__lock.notify_all()
        self.__lock.release()
        return qid

    # ------------------------------------------------------------------------
    def ray(self, qid: str) -> Ray:
        if self.__rays.get(qid) is None:
            ray = Ray(qid=qid)
            self.__rays[qid] = ray
        return self.__rays[qid]

    # ------------------------------------------------------------------------
    def rays(self, criteria=None) -> List[Ray]:
        rays: List[Ray] = []
        for qid, ray in self.__rays.items():
            if criteria is None or criteria(ray):
                rays.append(ray)
        return rays

    # ------------------------------------------------------------------------
    def pending_rays(self, criteria=None) -> List[str]:
        rays: List[str] = []
        for qid, ray in self.__rays.items():
            if criteria is None or criteria(ray):
                rays.append(ray)
        rays.sort(key=lambda r: r.created_at)
        return rays

    # ------------------------------------------------------------------------
    def process(self, qid):

        if self.__app is None:
            logging.error("Openfabric - no app configured!")
            traceback.print_exc()
            return

        with MeasureBlockTime("Engine::execution_callback_function"):
            ray = self.ray(qid)
            self.__app.execution_callback_function(None, ray)
        output = self.read(qid, 'out', OutputSchema().load)

        return output

    # ------------------------------------------------------------------------
    def delete(self, qid: str, app: App = None) -> Ray:
        self.__lock.acquire()
        self.__task.rem(qid)
        ray = self.ray(qid)
        if app is not None:
            app.cancel_execution(ray)
        else:
            self.__app.cancel_execution(ray)
        self.__store.drop(qid)
        self.__rays.pop(qid)
        ray.status = RayStatus.REMOVED
        self.__lock.notify_all()
        self.__lock.release()
        return ray

    # ------------------------------------------------------------------------
    def read(self, qid: str, key: str, deserializer=None) -> Any:
        output = self.__store.get(qid, key)
        if output is None:
            return None
        output = deserializer(output) if deserializer is not None else output
        return output

    # ------------------------------------------------------------------------
    def write(self, qid: str, key: str, val: Any, serializer=None):
        if val is not None:
            val = serializer(val) if serializer is not None else val
        self.__store.set(qid, key, val)

    def flush(self, qid: str):
        self.__store.flush(qid)


engine = Engine()
