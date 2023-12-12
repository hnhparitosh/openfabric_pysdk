import gevent
import pickle
import threading
import zmq

from openfabric_pysdk.context import State

class DispatchActions:
    ADD = 'add'
    CHECK = 'check'
    CONFIGURE = 'configure'
    EXIT = 'exit'
    FETCH = 'fetch'
    LOG = 'log'
    REMOVE = 'remove'
    APP_STATE = 'app_state'
    UPDATE = 'update'

class DispatchMessage:
    def __init__(self):
        pass

    @staticmethod
    def add(qid: str):
        return pickle.dumps({'action': DispatchActions.ADD, 'data': qid})

    @staticmethod
    def check_request(qid: str):
        return pickle.dumps({'action': DispatchActions.CHECK, 'data': qid})

    @staticmethod
    def configure():
        return pickle.dumps({'action': DispatchActions.CONFIGURE})

    @staticmethod
    def exit(reason: str):
        return pickle.dumps({'action': DispatchActions.EXIT, 'data': reason})

    @staticmethod
    def fetch(field: str):
        return pickle.dumps({'action': DispatchActions.FETCH, 'data': field})

    @staticmethod
    def log(level: int, message: str):
        data = {'level': level, 'message': message}
        return pickle.dumps({'action': DispatchActions.LOG, 'data': data})

    @staticmethod
    def remove(qid: str):
        return pickle.dumps({'action': DispatchActions.REMOVE, 'data': qid})
    
    @staticmethod
    def state_update(qid: str, input = None, output = None, ray = None):
        data = {'qid': qid}
        if  input is not None:
            data['input'] = input
        if  output is not None:
            data['output'] = output
        if  ray is not None:
            data['ray'] = ray

        return pickle.dumps({'action': DispatchActions.UPDATE, 'data': data})
    
    @staticmethod
    def app_state(state: str):
        return pickle.dumps({'action': DispatchActions.APP_STATE, 'data': state})

    @staticmethod
    def deserialize(input):
        data = pickle.loads(input)
        
        return data['action'], data['data'] if 'data' in data else None

class Publisher():
    def __init__(self, address = "tcp://127.0.0.1:5556"):
        context = zmq.Context()
        self.publisher_socket = context.socket(zmq.PUB)
        self.publisher_socket.bind(address)

    def publish(self, message):
        self.publisher_socket.send(message)
    
    def close(self):
        self.publisher_socket.close()
    
class Subscriber():
    def __init__(self, address = "tcp://127.0.0.1:5556", callback = None, geventEnv = False):
        context = zmq.Context()

        self.subscriber_socket = context.socket(zmq.SUB)
        self.subscriber_socket.connect(address)
        self.subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.running = True

        self.on_message_received_callback = callback
        if geventEnv:
            self.subscriber_greenlet = gevent.spawn(self.__message_handler2, self.subscriber_socket)
        else:
            self.__execution = threading.Thread(target=self.__message_handler, args=(self.subscriber_socket,))
            self.__execution.start()

    def __del__(self):
        pass
        self.running = False
        self.subscriber_socket.close()
        if self.__execution is not None:
            self.__execution.join()
        self.__execution = None

    def __message_handler(self, socket):
        while True:
            try:
                message = socket.recv(flags=zmq.NOBLOCK)
                if self.on_message_received_callback is not None:
                    self.on_message_received_callback(message)
            except zmq.Again:
                gevent.sleep(0.1)
                pass

    # Todo: try to switch to this message handler
    def __message_handler2(self, socket):
        while True:
            message = socket.recv()
            if self.on_message_received_callback is not None:
                self.on_message_received_callback(message)
            gevent.sleep(0.001)

    def register_callback(self, callback):
        self.on_message_received_callback = callback

    def close(self):
        self.subscriber_socket.close()
