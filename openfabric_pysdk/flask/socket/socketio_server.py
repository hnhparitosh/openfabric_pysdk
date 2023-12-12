from flask_socketio import SocketIO, Namespace
from openfabric_pysdk.flask.core import Webserver


#######################################################
#  SocketIOServer
#######################################################
class SocketIOServer(SocketIO):
    webserver: Webserver = None

    # ------------------------------------------------------------------------
    def __init__(self, webserver=None, **kwargs):
        super().__init__(webserver, **kwargs)
        self.webserver = webserver

    # ------------------------------------------------------------------------
    def run(self, host=None, port=None, **kwargs):
        super().run(self.webserver, host=host, port=port, **kwargs)
