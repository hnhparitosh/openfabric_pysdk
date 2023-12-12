import logging
from typing import Any, Dict, Set

from openfabric_pysdk.flask.core import Webserver, request
from openfabric_pysdk.flask.socket import Namespace, SocketIOServer, SocketIOClient
from openfabric_pysdk.service import SocketService
from openfabric_pysdk.transport import ResourceDescriptor


#######################################################
#  Execution Socket
#######################################################
class ExecutionSocket(Namespace):
    __url: str = None
    __sessions: Set[str] = None
    __webserver: Webserver = None
    __sioserver: SocketIOServer = None
    __sioclient: SocketIOClient = None

    # ------------------------------------------------------------------------
    def __init__(self, webserver: Webserver, descriptor: ResourceDescriptor):
        super().__init__(descriptor.endpoint)
        self.__sessions = set()
        self.__webserver = webserver
        self.__url = f"{descriptor.remote}/{descriptor.endpoint}"

    # ------------------------------------------------------------------------
    def run(self, debug: bool, host: str, port: int):
        self.__sioserver = SocketService.server(self.__webserver)
        self.__sioserver.on_namespace(self)
        self.__sioclient = SocketService.client(self.__url, namespaces=[self.namespace])
        app_context = self.__webserver.app_context()

        @self.__sioclient.on("restore", namespace=self.namespace)
        def _restore(data):
            with app_context:
                self.__sioserver.emit('restore', data, namespace=self.namespace)

        @self.__sioclient.on("state", namespace=self.namespace)
        def _state(data):
            with app_context:
                self.__sioserver.emit('state', data, namespace=self.namespace)

        @self.__sioclient.on("progress", namespace=self.namespace)
        def _progress(data):
            with app_context:
                self.__sioserver.emit('progress', data, namespace=self.namespace)

        @self.__sioclient.on("response", namespace=self.namespace)
        def _response(data):
            with app_context:
                self.__sioserver.emit('response', data, namespace=self.namespace)

        @self.__sioclient.on("submitted", namespace=self.namespace)
        def _submitted(data):
            with app_context:
                self.__sioserver.emit('submitted', data, namespace=self.namespace)

        self.__sioserver.run(host=host, debug=debug, port=port)

    # ------------------------------------------------------------------------
    def on_execute(self, data: bytes, background: bool):
        self.__sioclient.emit('execute', data=(data, background), namespace=self.namespace)

    # ------------------------------------------------------------------------
    def on_resume(self, uid: str):
        self.__sioclient.emit('resume', data=uid, namespace=self.namespace)

    # ------------------------------------------------------------------------
    def on_restore(self, qid: str):
        self.__sioclient.emit('restore', data=qid, namespace=self.namespace)

    # ------------------------------------------------------------------------
    def on_state(self, uid: str):
        self.__sioclient.emit('state', data=uid, namespace=self.namespace)

    # ------------------------------------------------------------------------
    def on_delete(self, qid: str):
        self.__sioclient.emit('delete', data=qid, namespace=self.namespace)

    # ------------------------------------------------------------------------
    def on_connect(self):
        sid = request.sid
        logging.debug(f'Openfabric - client connected {sid} on {request.host}')
        self.__sessions.add(sid)

    # ------------------------------------------------------------------------
    def on_disconnect(self):
        sid = request.sid
        logging.debug(f'Openfabric - client disconnected {sid} on {request.host}')
        self.__sessions.remove(sid)
