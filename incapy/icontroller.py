
from abc import ABC, abstractmethod


class IController(ABC):

    @abstractmethod
    def __init__(self, model):
        pass

    @abstractmethod
    def update_weights(self):
        # sends the data to the model and update the matrix every few seconds
        raise NotImplementedError()

    @abstractmethod
    def start_iteration(self):
        raise NotImplementedError()

    @abstractmethod
    def stop_iteration(self):
        raise NotImplementedError

    @abstractmethod
    def _iterate(self):
        # calculations for one time step
        raise NotImplementedError()
