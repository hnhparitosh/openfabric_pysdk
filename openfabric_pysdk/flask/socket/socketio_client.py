from socketio import Client


#######################################################
#  SocketIOClient
#######################################################
class SocketIOClient(Client):

    # ------------------------------------------------------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
