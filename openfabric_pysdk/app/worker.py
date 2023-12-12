#!/usr/bin/env python3
import logging
import os
import traceback

import argparse
import re
import time
import threading
import traceback
from typing import Any

import sys
sys.path.append(str({os.getcwd()}))
from comm import Subscriber, Publisher, DispatchMessage, DispatchActions

from openfabric_pysdk.benchmark import MeasureBlockTime
from openfabric_pysdk.context import MessageType, Ray, RaySchema, RayStatus, State, StateStatus, StateSchema
from openfabric_pysdk.loader import InputSchema, OutputSchema
from openfabric_pysdk.store import KeyValueDB
from openfabric_pysdk.loader.config import state_config
from openfabric_pysdk.loader import ConfigSchema

config_callback_function = None
execution_callback_function = None
suspend_callback_function = None

suspend_request_time_s = 5
loglevel = logging.DEBUG
current_qid = None
publisher = None
subscriber = None
worker = None
running = True
working = True
queue = []
lock: threading.Condition = threading.Condition()

def notify_ray_update(ray: Ray):
    logging.debug(f'notify_ray_update {ray}')
    publisher.publish(DispatchMessage.state_update(ray.qid, ray=RaySchema().dump(ray)))
    pass

class LogsHandler(logging.StreamHandler):
    level = loglevel
    def emit(self, record=None):
        if record is None:
            return
        try:
            msg = self.format(record)

            publisher.publish(DispatchMessage.log(record.levelno, msg))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

class Worker:
    __db__path: KeyValueDB = f"{os.getcwd()}/datastore"

    def __init__(self):
        self.state = State()

    # ------------------------------------------------------------------------
    def process(self, qid):

        with MeasureBlockTime("Engine::execution_callback_function"):
            kvdb = KeyValueDB(f"{qid}", path=self.__db__path, autodump=False)
            output = None
            ray = self.read(kvdb, 'ray', RaySchema().load)
            if ray is None:
                return

            if ray.finished == True and ray.status != RayStatus.REMOVED:
                output = self.read(kvdb, 'out', OutputSchema().load)
                publisher.publish(DispatchMessage.state_update(qid, output=OutputSchema().dump(output)))
                return

            ray.on_update(notify_ray_update)

            logging.info(f'processing {qid}')
            try:
                data = self.read(kvdb, 'in', InputSchema().load)
                if data is None:
                    return

                ray.status = RayStatus.RUNNING

                # Callback execution method
                output = execution_callback_function(data, ray, self.state)

                ray.status = RayStatus.COMPLETED
            except:
                error = f"process - failed executing: [{qid}]\n{traceback.format_exc()}"
                logging.error(error)
                ray.message(MessageType.ERROR, error)
                ray.status = RayStatus.FAILED
        publisher.publish(DispatchMessage.state_update(qid, output=OutputSchema().dump(output)))
        ray.complete()

        logging.info(f'completed {qid}')

    # ------------------------------------------------------------------------
    def read(self, kvdb: KeyValueDB, key: str, deserializer=None) -> Any:
        output = kvdb.get(key)
        if output is None:
            return None
        output = deserializer(output) if deserializer is not None else output
        return output

def process_line(line: str, skipConfig = False):
    global current_qid
    global queue
    global lock
    logging.debug(f'event {line}')

    pattern = re.compile(r'([0-9]+-[0-9]+-[0-9]+\/[0-9]+:[0-9]+) ([0-9a-zA-Z]+)[ ]+(.*)\n')
    event = re.search(pattern, line)
    
    if (event != None):
        date = event.group(1)
        action = event.group(2)
        data = event.group(3)
        logging.debug(f"Event: date: {date} action: {action} data: {data}")

        if action == "ADD":
            lock.acquire()
            if data != current_qid and data not in queue:
                queue.append(data)
            lock.release()
        elif action == "DEL":
            # TODO: Canceling an execution does not stop it if already started.
            # Status will be sent to the application after execution is completed.
            lock.acquire()
            try:
                while data in queue:
                    queue.remove(data)
            except:
                pass
            lock.release()
        elif action == "CFG":
            if not skipConfig:
                state = State()

                state_config.reload()
                items = state_config.all().items()
                config = dict(map(lambda kv: (kv[0], ConfigSchema().load(kv[1])), items))

                if config_callback_function is not None:
                    try:
                        config_callback_function(config, state)
                    except Exception as e:
                       logging.error(f"Openfabric - invalid configuration can\'t restored : {e}")
                else:
                    logging.warning(f"Openfabric - no configuration callback available")
        elif action == "START":
            logging.debug(f"Start event")
        elif action == "STATUS":
            logging.debug(f"App status {data}")
        else:
            logging.warn(f"Unknown action: {action}")
    else:
        logging.warn(f"Unknown event: {line}")

# would be the main thread
def execution():
    global suspend_request_time_s
    global current_qid
    global running
    global working
    global queue
    global lock
    retry_counter = 10 * suspend_request_time_s
    
    # TODO: use locks
    while running:
        lock.acquire()
        current_qid = None
        if len(queue) > 0:
            current_qid = queue.pop(0)
        lock.release()
        if current_qid is not None:
            working = True
            try:
                worker.process(current_qid)
            except:
                # TODO: fix this.
                # try catch should be in process, but it's relating to reading the db
                logging.error(f"Failed to execute {current_qid}")
                pass
            retry_counter = 10 * suspend_request_time_s
        else:
            if retry_counter > 0:
                retry_counter -= 1
            else:
                working = False

                # In practice we could implement a suspend_prepare and a suspend function
                # The suspend_prepare would be called before the suspend function once
                # the queue is empty.
                # After a predefined/fixed period we call the suspend function.
                # But the application could return False on the current suspend on the first
                # few calls and True on a later call. Basically the application could decide
                # to suspend, after a predefined period.
                if suspend_callback_function is not None:
                    try:
                        state = State()
                        # If the suspend function returns True, we exit the application.
                        if suspend_callback_function(state):
                            logging.info(f"Openfabric - suspend allowed by the application")
                            publisher.publish(DispatchMessage.exit("suspend"))
                            running = False
                            continue
                        else:
                            logging.debug(f"Openfabric - suspend denied by the application - retrying in 1 second")
                            # retry after 1 second
                            retry_counter = 10
                    except Exception as e:
                        logging.error(f"Openfabric - suspend ended with error : {e}")
                else:
                    # No point in retrying if there is no suspend callback
                    retry_counter = 99999999999

        time.sleep(0.1)

def message_received_callback(message):
    global current_qid
    global queue
    global lock
    global running
    action, data = DispatchMessage.deserialize(message)

    if action == None:
        logging.error("Missing action in message")
        return

    if action == DispatchActions.ADD or action == DispatchActions.CHECK:
        logging.debug(str(action) + ": " + str(data))
        lock.acquire()
        if data != current_qid and data not in queue:
            queue.append(data)
        lock.release()
    elif action == DispatchActions.REMOVE:
        logging.debug("REMOVE: " + str(data))
        lock.acquire()
        try:
            while data in queue:
                queue.remove(data)
        except:
            pass
        lock.release()
    elif action == DispatchActions.CONFIGURE:
        print("CONFIGURE: " + str(data))
        state = State()

        state_config.reload()
        items = state_config.all().items()
        config = dict(map(lambda kv: (kv[0], ConfigSchema().load(kv[1])), items))

        config_callback_function(config, state)
    elif action == DispatchActions.EXIT:
        running = False
    else:
        logging.error("Unexpected action: " + str(action))

if __name__ == "__main__":
    # Disable socketio and engineio logging
    # Reason: would cause recursion error as we are using the proxy to forward logs
    logging.getLogger("socketio").setLevel(logging.ERROR)
    logging.getLogger("engineio").setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(description='Worker')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    parser.add_argument('--publisher_port', type=int, default=5556, help='publisher port')
    parser.add_argument('--subscriber_port', type=int, default=5555, help='subscriber port')
    args = parser.parse_args()

    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    # Configure custom logging
    logger = logging.getLogger()
    logger.setLevel(loglevel) 
    custom_handler = LogsHandler()
    formatter = logging.Formatter("%(asctime)s: %(message)s")
    custom_handler.setFormatter(formatter)
    logger.addHandler(custom_handler)

    publisher = Publisher(f"tcp://127.0.0.1:{args.publisher_port}")
    subscriber = Subscriber(f"tcp://127.0.0.1:{args.subscriber_port}", message_received_callback)

    try:
        from openfabric_pysdk.api import config_callback_function, \
            execution_callback_function,                           \
            suspend_callback_function
        startup_error = None

        state = State()
        state.status = StateStatus.RUNNING
        publisher.publish(DispatchMessage.app_state(StateSchema().dump(state)))
    except Exception as inst:
        startup_error = ''.join(traceback.TracebackException.from_exception(inst).format())
        time.sleep(1)
        logging.error(f'Exception while starting app: {startup_error}')
        state = State()
        state.status = StateStatus.CRASHED
        publisher.publish(DispatchMessage.app_state(StateSchema().dump(state)))
        time.sleep(1)
        publisher = None
        subscriber = None
        exit(-1)

    worker = Worker()

    logging.info(f'started')

    exec = threading.Thread(target=execution)
    exec.start()

    while running:
        time.sleep(0.1)

    logging.info(f'exiting')
    exec.join()

    logger.removeHandler(custom_handler)

    # Need to close socket connection otherwise the app hands in state "sleeping"
    worker = None
    logging.info(f'stopped')
    exit(0)
