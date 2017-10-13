"""utils for servers"""

import codecs
import pickle


def serialize_data(func):
    """parse_data is a decorator which serialize incoming and outgoing data."""
    def _function_wrapper(*args):
        return _prepare_output(func(args[0], _prepare_input(args[-1])))

    return _function_wrapper


def _prepare_output(data):
    return codecs.encode(pickle.dumps(data), 'base64').decode()


def _prepare_input(data):
    return pickle.loads(codecs.decode(bytes(data, encoding='utf-8'), 'base64'))
