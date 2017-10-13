"""Server implementation."""


from .base import BaseServer
from .preparator import EchoPreparator
from .utils import serialize_data


class Server(BaseServer):
    """
    Server is a representation of a server.

    :param port: port in form of integer
    :param log: is logging enabled or not
    :param ml: interface of ml object, need to implement predict method
    :param address: address of a server, keep default value if you don't understand what it's for
    """

    def __init__(self, port, ml, address='0.0.0.0', preparator=EchoPreparator,
                 ml_config=None, log=True):
        if not any(method in dir(ml) for method in [
                'predict', 'train']):
            raise ValueError('ml must have predict or train method')

        if not all(method in dir(preparator) for method in [
                'prepare_output', 'prepare_input']):
            raise ValueError(
                'preparator must have prepare_output and prepare_input methods')

        super().__init__(port, ml, address, ml_config, log)

        self.set_dispatcher({
            'train': self._train,
            'predict': self._predict
        })

        self._preparator = preparator

    @serialize_data
    def _predict(self, data):
        return self._ml.predict(data)

    @serialize_data
    def _train(self, data):
        prepared_data = self._preparator.prepare_input(data)
        res = self._ml.train(prepared_data)
        prepared_res = self._preparator.prepare_output(res)
        return prepared_res
