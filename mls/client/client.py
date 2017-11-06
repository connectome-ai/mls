"""Client implementation."""


import os
from concurrent.futures import ThreadPoolExecutor

import requests

from .utils import _prepare_input, _prepare_output


class Client:
    """
    Client is a representation of a client.

    :param address: address of a server like http://localhost:3000
    """

    def __init__(self, address):
        self._address = os.path.join(address, 'jsonrpc')
        self._id = 0
        self._pool = ThreadPoolExecutor(1)

    def _increment_id(self):
        self._id += 1
        if self._id > 10 ** 8:
            self._id = 0

    def _send_request(self, method, data):

        response = requests.post(
            self._address,
            data=_prepare_input(data),
            headers={'method': method}
        )

        error = response.headers.get('error')
        if error != '':
            raise ValueError(error)

        return _prepare_output(response.content)

    def _ping(self):
        return self._send_request('ready', None)

    def ready(self):
        """
        ready tells if server is ready.

        :returns: true or false
        """
        try:
            return self._ping()
        except requests.exceptions.ConnectionError:
            return False

    def started(self):
        """
        sstarted tells if server started.

        :returns: true or false
        """
        try:
            _ = self._ping()
            return True
        except requests.exceptions.ConnectionError:
            return False

    def train(self, data):
        """
        train launches training ml algorithm on server on provided data.

        :param data: data to process
        """
        return self._pool.submit(self._send_request, 'train', data)

    def update(self, data):
        """
        update sends new data to state machine.

        :param data: data to process
        """

        return self._pool.submit(self._send_request, 'update', data)

    def set_state(self, data):
        """
        set_state sends new state data to state machine.

        :param data: data to process
        """

        return self._pool.submit(self._send_request, 'set_state', data)

    def predict(self, data):
        """
        predict launches prediction ml algorithm on server on provided data.

        :param data: data to process
        """

        return self._pool.submit(self._send_request, 'predict', data)
