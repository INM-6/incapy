
from abc import ABC, abstractmethod


class IView(ABC):
    @abstractmethod
    def __init__(self, model, controller):
        raise NotImplementedError()

    @abstractmethod
    def _register(self, model):
        raise NotImplementedError()

    @abstractmethod
    def update(self, data):
        raise NotImplementedError()
