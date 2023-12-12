import logging
from typing import Any, Dict, Set
from datetime import datetime

import gevent
import uuid
import copy

from openfabric_pysdk.app import App
from openfabric_pysdk.benchmark import MeasureBlockTime
from openfabric_pysdk.context import Ray, RaySchema, RayStatus, State, StateSchema
from openfabric_pysdk.engine import engine
from openfabric_pysdk.flask.core import Webserver, request
from openfabric_pysdk.flask.socket import Namespace, SocketIOServer, emit
from openfabric_pysdk.service import SocketService
from openfabric_pysdk.transport import ResourceDescriptor
from openfabric_pysdk.transport.schema import UserIdSchema
from openfabric_pysdk.utility import ChangeUtil, ZipUtil
from openfabric_pysdk.service import ConfigService


#######################################################
#  Execution Socket
#######################################################
class ExecutionSocket(Namespace):
    __app: App = None
    __sessions: Set[str] = None
    __webserver: Webserver = None
    __sioserver: SocketIOServer = None

    # ------------------------------------------------------------------------
    def __init__(self, webserver: Webserver, descriptor: ResourceDescriptor):
        super().__init__(descriptor.endpoint)
        self.__sessions = set()
        self.__app = descriptor.app
        self.__webserver = webserver

    # ------------------------------------------------------------------------
    def run(self, debug: bool, host: str, port: int):
        self.__sioserver = SocketService.server(self.__webserver)
        self.__sioserver.on_namespace(self)
        self.__sioserver.run(host=host, debug=debug, port=port)

    # ------------------------------------------------------------------------
    def on_configure(self, config: bytes):
        with MeasureBlockTime("Socket::configure"):
            sid = request.sid

            dictionary = ZipUtil.decompress(config)
            config = dictionary.get('body', None)
            header = dictionary.get('header', dict())
            uid = header.get('uid', None)
            user = UserIdSchema().load(dict(uid=uid))

            if config != None:
                ConfigService.write(self.__app, user, config)
            else:
                # Return existing configuration
                # TODO: or should we have the option to clear it?
                config = ConfigService.read(self.__app, user)

            emit('settings', dict(uid=uid, config=config))

    # ------------------------------------------------------------------------
    def on_execute(self, data: bytes, background: bool):
        with MeasureBlockTime("Socket::execute"):
            sid = request.sid

            dictionary = ZipUtil.decompress(data)
            data = dictionary.get('body', None)
            header = dictionary.get('header', dict())
            uid = header.get('uid', None)
            rid = header.get('rid', uuid.uuid4().hex)

            logging.info(f"Socket::execute: sid={sid}, uid={uid}, rid={rid}, background={background}")
            if background is True:
                self.__execute_background(data, sid, uid, rid)
            else:
                self.__execute_foreground(data, sid, uid, rid)

    def __execute_foreground(self, data: Any, sid: str, uid: str, rid: str):
        # Setup

        ray = engine.ray(sid)

        # Skip the same request while pending
        if ray.status != RayStatus.UNKNOWN and ray.status != RayStatus.REMOVED:
            return

        qid = engine.prepare(self.__app, data, qid=sid, sid=sid, uid=uid, rid=rid)
        ray = engine.ray(qid)
        # Execute in foreground
        with MeasureBlockTime("Socket::callback"):
            engine.process(qid)
            output = engine.read(qid, 'out')
            ray_dump = RaySchema().dump(ray)
            engine.delete(qid, self.__app)
            emit('response', dict(output=output, ray=ray_dump))

    def __execute_background(self, data: str, sid: str, uid: str, rid: str):
        maximum_update_interval = 3 # seconds
        # Setup
        qid = engine.prepare(self.__app, data, sid=sid, uid=uid, rid=rid)
        ray = engine.ray(qid)
        prevRay = None
        emit('submitted', RaySchema().dump(ray))

        last_update = now = datetime.now()

        # Execute in background
        with MeasureBlockTime("Socket::callback"):
            while sid in self.__sessions:
                if prevRay == None or prevRay.updated_at != ray.updated_at:
                    try:
                        prevRay = copy.deepcopy(ray)

                        ray_dump = RaySchema().dump(ray)
                        emit('progress', ray_dump)
                        last_update = datetime.now()
                    except:
                        # Failed to copy ray. Downside is that same message will be sent again.
                        pass

                if (datetime.now() - last_update).total_seconds() > maximum_update_interval:
                    last_update = datetime.now()
                    ray_dump = RaySchema().dump(ray)
                    emit('progress', ray_dump)

                if ray.finished is True:
                    ray_dump = RaySchema().dump(ray)
                    # input = background.get(qid, 'in')
                    output = engine.read(qid, 'out')
                    emit('response', dict(output=output, ray=ray_dump))
                    break

                gevent.sleep(0.1)

    # ------------------------------------------------------------------------
    def on_resume(self, uid: str):
        sid = request.sid
        with MeasureBlockTime("OpenfabricSocket::restore"):
            def criteria(_ray: Ray):
                # is deleted ?
                if _ray is None:
                    return False
                # is different user ?
                if _ray.uid != uid:
                    return False
                # is an active session available ?
                if _ray.sid in self.__sessions and _ray.sid != sid:
                    return False
                return True

            # Filter rays
            rays = engine.pending_rays(criteria)
            for ray in rays:
                emit('progress', RaySchema().dump(ray))

    # ------------------------------------------------------------------------
    def on_restore(self, qid: str):
        ray_dump = engine.read(qid, 'ray')
        input_dump = engine.read(qid, 'in')
        output_dump = engine.read(qid, 'out')
        emit('restore', dict(input=input_dump, output=output_dump, ray=ray_dump))

    # ------------------------------------------------------------------------
    def on_state(self, uid: str):
        sid = request.sid
        with MeasureBlockTime("Socket::state"):
            while sid in self.__sessions:
                changed = ChangeUtil.is_changed('execution::state' + sid, self.__app.state, StateSchema().dump)
                if changed is True:
                    emit('state', StateSchema().dump(self.__app.state))
                gevent.sleep(0.1)

    # ------------------------------------------------------------------------
    def on_delete(self, qid: str):
        sid = request.sid
        with MeasureBlockTime("OpenfabricSocket::delete"):
            engine.delete(qid, self.__app)

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
