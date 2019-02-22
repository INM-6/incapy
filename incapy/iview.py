
from abc import ABC, abstractmethod


class IView(ABC):
    """
    Abstract base class / interface for the view.

    """

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

    @abstractmethod
    def update_ui(self, msg, value):
        raise NotImplementedError

    # Notify everyone who needs to know about any events
    @abstractmethod
    def add_event_listener(self, listener):
        raise NotImplementedError

    @abstractmethod
    def show(self):
        raise NotImplementedError()
