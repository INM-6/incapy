
from abc import ABC, abstractmethod


class IView(ABC):
    @abstractmethod
    def __init__(self, model):
        pass

    @abstractmethod
    def _register(self, model):
        raise NotImplementedError()

    @abstractmethod
    def _unregister(self, model):
        raise NotImplementedError()

    @abstractmethod
    def update(self, data):
        raise NotImplementedError()

    # XXX
    @abstractmethod
    def add_event_listener(self, listener):
        raise NotImplementedError
