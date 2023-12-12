import logging
import os
import subprocess
import gevent
import random
from typing import Any, Dict
from pathlib import Path

from openfabric_pysdk.context import Ray, State, StateStatus, RaySchema, RayStatus, StateSchema
from openfabric_pysdk.loader import ConfigClass, InputClass, OutputClass
from openfabric_pysdk.loader.config import manifest, state_config
from openfabric_pysdk.store import KeyValueDB

from .comm import Subscriber, Publisher, DispatchMessage, DispatchActions

my_env = os.environ.copy()
if "PYTHONPATH" in my_env:
    my_env["PYTHONPATH"] = f"{os.getcwd()}:{my_env['PYTHONPATH']}"
else:
    my_env["PYTHONPATH"] = os.getcwd()

#######################################################
#  App
#######################################################
class App:
    state: State = None
    __process = None
    __file_path = "actions.log"
    __script_dir = Path( __file__ ).parent.absolute()

    # ------------------------------------------------------------------------
    def __init__(self):
        self.state = State()
        self.publisher_port = random.randint(5001, 9999)
        self.subscriber_port = self.publisher_port + 1
        self.publisher = Publisher(f"tcp://127.0.0.1:{self.publisher_port}")
        self.subscriber = Subscriber(f"tcp://127.0.0.1:{self.subscriber_port}", self.__message_received_callback)
        self.dispatch("START", "app")
    
    # ------------------------------------------------------------------------
    def __del__(self):
        # TODO: could signal 
        #    self.publisher.publish(DispatchMessage.exit("closing"))
        # in order to have a graceful shutdown
        # if no response after a period of time, kill self.__process
        # stop publisher and subscriber
        pass

    # ------------------------------------------------------------------------
    def __message_received_callback(self, message):
        from openfabric_pysdk.engine import engine
        action, data = DispatchMessage.deserialize(message)

        if action == None:
            logging.error("Missing action in message")
            return

        if action == DispatchActions.FETCH:
            if data == "queue":
                logging.debug("FETCH: " + str(data))
                self.publisher.publish(DispatchMessage.state_update(DispatchActions.FETCH, data))
            else:
                logging.error("Unknown fetch request: " + str(data))
        elif action == DispatchActions.UPDATE:
            response: Dict[str, Any] = data

            if 'qid' not in response:
                logging.error("Missing qid in message")
                return

            qid = response["qid"]
            logging.debug("UPDATE: " + str(qid))

            flushData = False
            if 'output' in response:
                engine.write(qid, "out", response['output'])
                flushData |= True

            if 'input' in response:
                engine.write(qid, "in", response['input'])
                flushData |= True

            if 'ray' in response:
                ray = RaySchema().load(response['ray'])
                engine.ray(ray.qid).update(ray)
                engine.write(qid, "ray", response['ray'])
                flushData |= ray.finished
            else:
                ray = engine.ray(qid)

            if ray is not None and flushData:
                engine.flush(qid)

        elif action == DispatchActions.APP_STATE:
            receivedState = StateSchema().load(data)
            logging.info(f"State update: {self.state.status} -> {receivedState['status']}")
            self.state.status = receivedState["status"]

        elif action == DispatchActions.LOG:
            logging.log(data['level'], f"Worker-log: {data['message']}")
        elif action == DispatchActions.EXIT:
            logging.info("Worker exited with reason: " + str(data))
            # Temporary workaround
            self.__process.kill()
            self.__process = None
        else:
            logging.error("Unexpected action: " + str(action))

    # ------------------------------------------------------------------------
    def set_status(self, status: StateStatus):
        self.state.status = status
        self.dispatch("STATUS", status, False)

    # ------------------------------------------------------------------------
    def dispatch(self, event, data="", start_worker=True):
        logging.debug(f"Dispatching {event} {data}")

        if start_worker:
            self.__update_worker_state()

        if event == "ADD":
            self.publisher.publish(DispatchMessage.add(data))
        elif event == "DEL":
            self.publisher.publish(DispatchMessage.remove(data))
        elif event == "CFG":
            self.publisher.publish(DispatchMessage.configure())
        elif event == "CHK":
            self.publisher.publish(DispatchMessage.check_request(data))

    # ------------------------------------------------------------------------
    def __update_worker_state(self):
        if self.__process is None or self.__process.poll() is not None:
            self.dispatch("START", "worker", False)
            # Note: remove stdout/stderr redirection to debug app
            # self.__process = subprocess.Popen(["python3", self.__script_dir / "worker.py", "--publisher_port", str(self.subscriber_port), "--subscriber_port", str(self.publisher_port)], env=my_env)
            self.__process = subprocess.Popen(["python3", self.__script_dir / "worker.py", "--publisher_port", str(self.subscriber_port), "--subscriber_port", str(self.publisher_port)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, env=my_env)

    # ------------------------------------------------------------------------
    def execution_callback_function(self, input: InputClass, ray: Ray) -> OutputClass:
        self.dispatch("ADD", ray.qid)
        counter = 0

        while True:
            if (ray.finished != True):
                gevent.sleep(0.1)
                counter += 1
                # Make sure the worker was not closing while we
                # were proposing a new entry, or that it died.
                if counter % 10 == 0:
                    self.dispatch("CHK", ray.qid)

                # If the app crashed, cancel all ongoing rays.
                if self.state.status == StateStatus.CRASHED:
                    ray.status = RayStatus.FAILED
                    ray.finished = True
                    break
            else:
                break

        return None

    # ------------------------------------------------------------------------
    def cancel_execution(self, ray: Ray):
        ray.status = RayStatus.CANCELED
        ray.complete()
        self.dispatch("DEL", ray.qid, False)

    # ------------------------------------------------------------------------
    def config_callback_function(self, config: Dict[str, ConfigClass]):
        self.dispatch("CFG", "reload", False)

    # ------------------------------------------------------------------------
    def get_manifest(self) -> KeyValueDB:
        return manifest

    # ------------------------------------------------------------------------
    def get_state_config(self) -> KeyValueDB:
        return state_config
