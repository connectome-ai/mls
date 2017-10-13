"""Client implementation."""


import json
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
        payload = {
            'method': method,
            'params': [_prepare_input(data)],
            'jsonrpc': '2.0',
            'id': self._id,
        }

        self._increment_id()

        response = requests.post(
            self._address,
            data=json.dumps(payload),
            headers={'content-type': 'application/json'}
        ).json()

        if response.get('error', None) is not None:
            raise ValueError(response['error'])

        return _prepare_output(response['result'])

    def ready(self):
        """
        ready tells if server is ready.

        :returns: true or false
        :raises: raises ConnectionError if server is down
        """
        payload = {
            'method': 'ready',
            'params': [],
            'jsonrpc': '2.0',
            'id': self._id,
        }

        self._increment_id()

        response = requests.post(
            self._address,
            data=json.dumps(payload),
            headers={'content-type': 'application/json'}
        ).json()

        return response['result']

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
