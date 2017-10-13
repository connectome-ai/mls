"""StateMachine implementation."""

from .base import BaseServer
from .utils import serialize_data


class StateMachine(BaseServer):
    """
    StateMachine is a representation of a state machine.

    :param port: port in form of integer
    :param log: is logging enabled or not
    :param ml: interface of ml object, need to implement predict method
    :param address: address of a server, keep default value if you don't understand what it's for
    """

    def __init__(self, port, ml, address='0.0.0.0',
                 ml_config=None, log=True):
        if not all(method in dir(ml) for method in [
                'update', 'set_state']):
            raise ValueError('ml must have update and set_state method')

        super().__init__(port, ml, address, ml_config, log)

        self.set_dispatcher({
            'update': self._update,
            'set_state': self._set_state
        })

    @serialize_data
    def _update(self, data):
        return self._ml.update(data)

    @serialize_data
    def _set_state(self, data):
        return self._ml.set_state(data)
