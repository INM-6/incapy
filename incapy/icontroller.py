
from abc import ABC, abstractmethod


class IController(ABC):
    """
    Abstract base class / interface for the controller.

    """

    @abstractmethod
    def __init__(self, model):
        pass

    @abstractmethod
    def next_window(self, value=None):
        with open("test1", mode="w+") as f:
            print("In parent", file=f)
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
