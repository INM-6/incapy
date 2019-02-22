
from abc import ABC, abstractmethod


class IModel(ABC):
    """
    Abstract base class / interface for the model.

    """

    @abstractmethod
    def __init__(self):
        pass

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
    def set_vertex_ids(self, data):
        raise NotImplementedError()

    @abstractmethod
    def set_edges(self, edges):
        raise NotImplementedError()

    @abstractmethod
    def set_edge_threshold_mask(self, mask):
        raise NotImplementedError()
