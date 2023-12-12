import logging
import os
import traceback

from openfabric_pysdk.flask import *
from openfabric_pysdk.loader import *
from openfabric_pysdk.app import App
from openfabric_pysdk.context import StateStatus
from openfabric_pysdk.execution import Container, Profile


@webserver.route("/")
def index():
    return render_template("index.html", manifest=manifest.all())


class Starter:

    # ------------------------------------------------------------------------
    @staticmethod
    def ignite(debug: bool, host: str, port=5000, remote: str = None):
        # Setup logger
        logger = logging.getLogger()
        if debug is True:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            logging.getLogger('socketio').setLevel(logging.ERROR)
            logging.getLogger('engineio').setLevel(logging.ERROR)

        # Profile
        profile = Profile()
        profile.host = host
        profile.port = port
        profile.debug = debug
        profile.remote = remote if remote is not None else os.getenv('RAI_URL')

        # Start app execution
        app = App()
        try:
            app.set_status(StateStatus.STARTING)
            container = Container(profile, webserver)
            container.start(app)
        except:
            app.set_status(StateStatus.CRASHED)
            logging.error(f"Openfabric - failed starting app: \n{traceback.format_exc()}")
