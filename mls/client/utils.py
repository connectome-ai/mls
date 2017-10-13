"""utils for clients"""

import codecs
import pickle


def _prepare_input(data):
    return codecs.encode(pickle.dumps(data), 'base64').decode()


def _prepare_output(data):
    return pickle.loads(codecs.decode(bytes(data, encoding='utf-8'), 'base64'))
