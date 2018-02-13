"""BaseServer implementation."""


import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

# from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from .utils import serialize_data


class BaseServer:
    """
    Server is a representation of a server.

    :param port: port in form of integer
    :param ml: interface of ml object, need to implement predict method
    :param log: turn logging off or on. True by default.
    :param address: address of a server, keep default value if you don't understand what it's for
    """

    def __init__(self, port, ml, address='0.0.0.0', ml_config=None, log=True):
        if not log:
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
            for name, _ in logging.Logger.manager.loggerDict.items():
                if any([x in name for x in ['requests', 'werkzeug', 'urllib']]):
                    logging.getLogger(name).setLevel(logging.ERROR)
        self._address = address
        self._port = port
        self._pool = ThreadPoolExecutor(1)
        self._dispatcher = {}

        self._ml_config = ml_config
        if ml_config is not None:
            self._ml_constructor = ml
            self._ml = None
        else:
            self._ml = ml

        self.set_dispatcher({'ready': self._ready})

    def _init_ml(self):
        self._ml = self._ml_constructor(**self._ml_config)

    @serialize_data
    def _ready(self, _):
        return self._ml is not None

    def set_dispatcher(self, route_table, clear=False):
        """
        set_dispatcher sets dispacther keys and values.

        :param route_table: route_table is a dict with keys as routes and values as callables
        """

        if clear:
            self._dispatcher = {}
        for route, func in route_table.items():
            self._dispatcher[route] = func

        return self

    @staticmethod
    def _init_cb(future):
        if future.exception() is not None:
            raise RuntimeError(future.exception())

    def __call__(self):
        if self._ml_config is not None:
            self._pool.submit(self._init_ml).add_done_callback(self._init_cb)

        @Request.application
        def _application(request):
            # dispatcher is dictionary {<method_name>: callable}
            method = request.headers['method']
            headers = {'error': ''}

            try:
                response = self._dispatcher[method](request.data)
            except Exception as e:
                response = b''
                headers['error'] = str(e)
                logging.critical(str(e))
                error = traceback.format_exc()
                logging.critical(error)

            return Response(response, headers=headers)

        run_simple(self._address, self._port, _application)
