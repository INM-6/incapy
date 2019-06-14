
from abc import ABC, abstractmethod


class IController(ABC):
    """
    Abstract base class / interface for the controller.

    """

    @abstractmethod
    def __init__(self, model, view):
        pass

    @abstractmethod
    def value_changed(self, msg, value=None):
        raise NotImplementedError()

    @abstractmethod
    def notify_event(self, msg):
        raise NotImplementedError()

    @abstractmethod
    def next_window(self, value=None):
        # sends the data to the model and update the matrix every few seconds
        raise NotImplementedError()

    @abstractmethod
    def start_iteration(self):
        raise NotImplementedError()

    @abstractmethod
    def stop_iteration(self):
        raise NotImplementedError()

    @abstractmethod
    def pause_iteration(self):
        raise NotImplementedError()

    @abstractmethod
    def continue_iteration(self):
        raise NotImplementedError()
