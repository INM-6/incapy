
from abc import ABC, abstractmethod


class IModel(ABC):

    @abstractmethod
    def __init__(self):
        raise NotImplementedError()

    @abstractmethod
    def add_listener(self, view):
        raise NotImplementedError()

    @abstractmethod
    def _update_view(self):
        raise NotImplementedError()

    @abstractmethod
    def set_positions(self, data):
        raise NotImplementedError()

    @abstractmethod
    def set_weights(self, data):
        raise NotImplementedError()

    # might not be needed
    @abstractmethod
    def set_ids(self, data):
        raise NotImplementedError()
