# pylint: skip-file

import os
import unittest
from datetime import datetime, timedelta
from multiprocessing import Process
from time import sleep

import numpy as np

from mls import Client, Server, StateMachine

TEST_ALL = os.getenv('TEST_ALL')
STEP_TIME = 0.1
SHORTER_SLEEP_TIME = 0.3
SLEEP_TIME = SHORTER_SLEEP_TIME + STEP_TIME
LONGER_SLEEP_TIME = SLEEP_TIME + STEP_TIME


def _sync_call(addr, data):
    client = Client(address=addr)
    res = client.predict(data)
    _ = res.result()


class FittingInterface:

    def __init__(self, long_predict=False, long_init=False):
        self._long_predict = long_predict
        if long_init:
            sleep(SLEEP_TIME)

    def predict(self, data):
        if self._long_predict:
            sleep(SLEEP_TIME)

        return data

    def update(self, data):
        return None

    def set_state(self, data):
        return None

    def train(self, data):
        if self._long_predict:
            sleep(SLEEP_TIME)

        return data


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        a = [[255, 128,   3],
             [255, 127,   2],
             [253, 125,   0]]
        cls._data = np.array([[[a, a, a], [a, a, a]], [[a, a, a], [a, a, a]]])
        cls._short_server = Server(
            port=36789, ml=FittingInterface(), log=False)
        cls._short_server_address = 'http://localhost:36789'
        cls._pr1 = Process(target=cls._short_server)
        cls._long_server = Server(
            port=36790, ml=FittingInterface(True), log=False)
        cls._pr2 = Process(target=cls._long_server)
        cls._long_server_address = 'http://localhost:36790'
        cls._sm = StateMachine(
            port=36791, ml=FittingInterface(False), log=False)
        cls._pr3 = Process(target=cls._sm)
        cls._sm_address = 'http://localhost:36791'
        cls._pr1.start()
        cls._pr2.start()
        cls._pr3.start()

    @classmethod
    def tearDownClass(cls):
        cls._pr1.terminate()
        cls._pr2.terminate()
        cls._pr3.terminate()

    def test_bad_server_init(self):
        s = Server(port=36710, ml=FittingInterface, ml_config={
                   'shit': False, 'poop': True})
        with self.assertRaises(RuntimeError):
            s()

    def test_sm(self):
        client = Client(address=self._sm_address)
        client.set_state(self._data)
        client.update(self._data)

    def test_ml(self):
        ml = FittingInterface.__init__(FittingInterface, **{
            'long_predict': False, 'long_init': True})

    def test_ready(self):
        s = Server(port=36794, ml=FittingInterface, ml_config={
                   'long_predict': False, 'long_init': True})
        pr = Process(target=s)
        client = Client(address='http://localhost:36794')
        self.assertFalse(client.started())

        res = client.predict(self._data)
        self.assertIsNotNone(res.exception())
        pr.start()
        while not client.started():
            pass
        self.assertFalse(client.ready())
        while not client.ready():
            pass
        self.assertTrue(client.ready())
        pr.terminate()

    def test_ready_safe(self):
        s = Server(port=36795, ml=FittingInterface, ml_config={
                   'long_predict': False, 'long_init': True})
        pr = Process(target=s)
        client = Client(address='http://localhost:36795')
        pr.start()
        while not client.ready():
            pass
        pr.terminate()

    def test_init_ml(self):
        Server(port=36795, ml=FittingInterface, ml_config={})

    def test_interface(self):
        with self.assertRaises(ValueError):
            Server(port=36789, ml='test')

    def test_train(self):
        client = Client(address=self._short_server_address)
        res = client.train(self._data)
        self.assertListEqual(res.result().tolist(), self._data.tolist())

    def test_server_sync(self):
        client = Client(address=self._short_server_address)
        res = client.predict(self._data)
        self.assertListEqual(res.result().tolist(), self._data.tolist())

    def test_server_sync_long(self):
        client = Client(address=self._long_server_address)
        now = datetime.now()
        res = client.predict(self._data)
        res = res.result()
        self.assertTrue(datetime.now() - now >
                        timedelta(seconds=SLEEP_TIME - STEP_TIME))
        self.assertListEqual(res.tolist(), self._data.tolist())

    def test_server_async(self):
        client = Client(address=self._long_server_address)
        now = datetime.now()
        res = client.predict(self._data)
        self.assertFalse(res.done())
        sleep(LONGER_SLEEP_TIME)
        self.assertListEqual(res.result().tolist(), self._data.tolist())

    def test_multi_client(self):
        client1 = Client(address=self._long_server_address)
        client2 = Client(address=self._long_server_address)

    def test_server_multi_requests_one_source(self):
        client1 = Client(address=self._long_server_address)
        client2 = Client(address=self._long_server_address)
        while not client1.ready() and not client2.ready():
            pass
        res1 = client1.predict(self._data)
        sleep(SHORTER_SLEEP_TIME)
        res2 = client2.predict(self._data)
        self.assertFalse(res1.done())
        self.assertFalse(res2.done())
        sleep(SLEEP_TIME - SHORTER_SLEEP_TIME + STEP_TIME)
        self.assertTrue(res1.done())
        self.assertFalse(res2.done())
        sleep(SLEEP_TIME)
        self.assertTrue(res1.done())
        self.assertTrue(res2.done())

    def test_server_multi_requests_different_sources(self):
        pr1 = Process(target=_sync_call, args=(
            self._long_server_address, self._data,))
        pr2 = Process(target=_sync_call, args=(
            self._long_server_address, self._data,))
        now = datetime.now()
        pr1.start()
        pr2.start()
        pr1.join()
        pr2.join()
        self.assertTrue(datetime.now() - now >
                        timedelta(seconds=SLEEP_TIME * 2 - STEP_TIME))

    def test_callback(self):
        client = Client(address=self._long_server_address)
        res = client.predict(self._data)
        res.add_done_callback(
            lambda x: self.assertListEqual(x.result().tolist(), self._data.tolist()))
        sleep(LONGER_SLEEP_TIME)


if __name__ == '__main__':
    unittest.main()
