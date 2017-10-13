# pylint: skip-file

import os
import unittest
from datetime import datetime, timedelta
from multiprocessing import Process
from time import sleep

import numpy as np

from mls import Client, Server, StateMachine

TEST_ALL = os.getenv('TEST_ALL')


def _sync_call(addr, data):
    client = Client(address=addr)
    res = client.predict(data)
    _ = res.result()


class FittingInterface:

    def __init__(self, long_predict=False, long_init=False):
        self._long_predict = long_predict
        if long_init:
            sleep(1)

    def predict(self, data):
        if self._long_predict:
            sleep(1)

        return data

    def update(self, data):
        return None

    def set_state(self, data):
        return None

    def train(self, data):
        if self._long_predict:
            sleep(1)

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
        with self.assertRaises(Exception):
            client.ready()

        res = client.predict(self._data)
        self.assertIsNotNone(res.exception())
        pr.start()
        while True:
            try:
                is_ready = client.ready()
                break
            except:
                pass
        self.assertFalse(is_ready)
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
        sleep(0.2)
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
        self.assertTrue(datetime.now() - now > timedelta(seconds=0.7))
        self.assertListEqual(res.tolist(), self._data.tolist())

    def test_server_async(self):
        client = Client(address=self._long_server_address)
        now = datetime.now()
        res = client.predict(self._data)
        self.assertFalse(res.done())
        sleep(1.2)
        self.assertListEqual(res.result().tolist(), self._data.tolist())

    def test_multi_client(self):
        client1 = Client(address=self._long_server_address)
        client2 = Client(address=self._long_server_address)

    @unittest.skipIf(TEST_ALL is None, 'short pipiline')
    def test_server_multi_requests_one_source(self):
        client1 = Client(address=self._long_server_address)
        client2 = Client(address=self._long_server_address)
        res1 = client1.predict(self._data)
        sleep(0.3)
        res2 = client2.predict(self._data)
        self.assertFalse(res1.done())
        self.assertFalse(res2.done())
        sleep(1)
        self.assertTrue(res1.done())
        self.assertFalse(res2.done())
        sleep(1.2)
        self.assertTrue(res1.done())
        self.assertTrue(res2.done())

    @unittest.skipIf(TEST_ALL is None, 'short pipiline')
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
        self.assertTrue(datetime.now() - now > timedelta(seconds=1.9))

    @unittest.skipIf(TEST_ALL is None, 'short pipiline')
    def test_callback(self):
        client = Client(address=self._long_server_address)
        res = client.predict(self._data)
        res.add_done_callback(
            lambda x: self.assertListEqual(x.result().tolist(), self._data.tolist()))
        sleep(1.2)


if __name__ == '__main__':
    unittest.main()
