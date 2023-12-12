import logging
from typing import List

from openfabric_pysdk.flask.core import Webserver
from openfabric_pysdk.flask.socket import SocketIOClient, SocketIOServer
from openfabric_pysdk.transport import ResourceDescriptor


#######################################################
#  Socket service
#######################################################
class SocketService:

    # ------------------------------------------------------------------------
    @staticmethod
    def install(descriptor: ResourceDescriptor, webserver: Webserver):
        logging.info(f"Openfabric - install Execution SOCKET endpoints on {descriptor.endpoint}")
        return descriptor.handler(webserver, descriptor)

    # ------------------------------------------------------------------------
    @staticmethod
    def server(webserver: Webserver):
        # Set this variable to "threading", "eventlet" or "gevent" to test the
        # different async modes, or leave it set to None for the application to choose
        # the best option based on installed packages.
        async_mode = "gevent"
        max_size = 10000000 * 100  # 100Mb
        return SocketIOServer(
            webserver=webserver,
            async_mode=async_mode,
            cors_allowed_origins='*',
            max_http_buffer_size=max_size
        )

    # ------------------------------------------------------------------------
    @staticmethod
    def client(url: str, namespaces: List[str]):
        client = SocketIOClient()
        client.connect(url, namespaces=namespaces)
        return client

    # ------------------------------------------------------------------------
    @staticmethod
    def create_portal(source: [SocketIOServer, SocketIOClient], target: [SocketIOServer, SocketIOClient],
                      namespace: str, webserver: Webserver, events: List[str]):
        app_context = webserver.app_context()

        def _bind_handler(event_name):
            @source.on(event_name, namespace=namespace)
            def _handler(*args):
                with app_context:
                    target.emit(event_name, *args, namespace=namespace)

        for event in events:
            _bind_handler(event)
