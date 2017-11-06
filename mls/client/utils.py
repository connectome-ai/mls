"""utils for clients"""

import pickle


def _prepare_input(data):
    return pickle.dumps(data)


def _prepare_output(data):
    return pickle.loads(data)
