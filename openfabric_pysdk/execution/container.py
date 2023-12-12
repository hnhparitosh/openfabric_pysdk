from typing import Any

from openfabric_pysdk.app import App
from openfabric_pysdk.context import StateStatus
from openfabric_pysdk.flask import Webserver
from openfabric_pysdk.flask import WebserverRestAPI, WebserverRestDoc
from openfabric_pysdk.loader import ConfigSchema
from openfabric_pysdk.service import ConfigService, RestService, SocketService, SwaggerService
from openfabric_pysdk.transport import ResourceDescriptor
from openfabric_pysdk.transport.socket.remote import ExecutionSocket as RemoteExecutionSocket
from openfabric_pysdk.transport.socket.local import ExecutionSocket as LocalExecutionSocket

from .profile import Profile


#######################################################
#  Container
#######################################################
class Container:
    __profile: Profile = None
    __websocket: [RemoteExecutionSocket, LocalExecutionSocket] = None
    __webserver: Webserver = None
    __rest: WebserverRestAPI = None
    __docs: WebserverRestDoc = None

    # ------------------------------------------------------------------------
    def __init__(self, profile: Profile, webserver: Webserver):
        self.__profile = profile
        self.__webserver = webserver
        self.__rest = WebserverRestAPI(webserver)
        self.__docs = WebserverRestDoc(webserver)

    # ------------------------------------------------------------------------
    def start(self, app: App):
        # Expose services
        self.__expose_swagger(app)
        self.__expose_rest(app)
        self.__expose_socket(app)
        # Apply configuration
        ConfigService.apply(app)

        app.set_status(StateStatus.RUNNING)

        # Start container
        # this will start eventing
        self.__websocket.run(
            debug=self.__profile.debug,
            host=self.__profile.host,
            port=self.__profile.port
        )

    # ------------------------------------------------------------------------
    def __expose_swagger(self, app: App):
        descriptor = self.__descriptor(app=app)
        SwaggerService.install(descriptor, webserver=self.__webserver)

    # ------------------------------------------------------------------------
    def __expose_socket(self, app: App):
        remote = self.__profile.remote
        if remote is None:
            from openfabric_pysdk.transport.socket.local import ExecutionSocket
        else:
            from openfabric_pysdk.transport.socket.remote import ExecutionSocket

        descriptor = self.__descriptor(handler=ExecutionSocket, endpoint='/app', app=app)
        self.__websocket = SocketService.install(descriptor, webserver=self.__webserver)

    # ------------------------------------------------------------------------
    def __expose_rest(self, app: App):

        remote = self.__profile.remote

        if remote is None:
            from openfabric_pysdk.transport.rest.local import \
                ConfigApi, \
                ExecutionApi, \
                ManifestApi, \
                BenchmarkApi, \
                QueueGetApi, QueuePostApi, QueueListApi, QueueDeleteApi
            from openfabric_pysdk.transport.socket.local import ExecutionSocket
        else:
            from openfabric_pysdk.transport.rest.remote import \
                ConfigApi, \
                ExecutionApi, \
                ManifestApi, \
                BenchmarkApi, \
                QueueGetApi, QueuePostApi, QueueListApi, QueueDeleteApi
            from openfabric_pysdk.transport.socket.remote import ExecutionSocket

        self.__install_rest(ExecutionApi, '/execution', app)
        self.__install_rest(ManifestApi, '/manifest', app)
        self.__install_rest(BenchmarkApi, '/benchmark', app)
        self.__install_rest(QueueGetApi, '/queue/get', app)
        self.__install_rest(QueueListApi, '/queue/list', app)
        self.__install_rest(QueuePostApi, '/queue/post', app)
        self.__install_rest(QueueDeleteApi, '/queue/delete', app)

        if ConfigSchema is not None:
            self.__install_rest(ConfigApi, '/config', app)

    # ------------------------------------------------------------------------
    def __install_rest(self, handler: type, endpoint: str, app: App):
        descriptor = self.__descriptor(handler=handler, endpoint=endpoint, app=app)
        RestService.install(descriptor, rest=self.__rest, docs=self.__docs)

    # ------------------------------------------------------------------------
    def __descriptor(self, handler=None, endpoint=None, app=None):
        descriptor = ResourceDescriptor()
        descriptor.app = app
        descriptor.handler = handler
        descriptor.endpoint = endpoint
        descriptor.remote = self.__profile.remote
        return descriptor
