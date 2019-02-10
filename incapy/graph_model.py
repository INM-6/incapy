from .imodel import IModel
import numpy as np

class GraphModel(IModel):

    def __init__(self):
        super().__init__()
        # XXX For signalling stop
        self.stop = False
        self.edges = np.ndarray((0, 2))
        # mapping from vertex_indices to matrix_indices!! (e.g. missing node)
        self.edge_weights = []
        self.vertex_ids = []
        self.vertex_pos = []
        self.listeners = []
        # Mapping from internal array indices to external IDs
        self.vertex_id_to_index = {}
        self.vertex_index_to_id = {}

    def add_listener(self, view):
        self.listeners.append(view)

    def _update_view(self):
        for l in self.listeners:
            l.update(((self.edges.T[0], self.edges.T[1]), (np.array(self.vertex_pos), self.vertex_ids)))

    def set_positions(self, positions):
        """

        :param positions: Numpy 2D array, shape (X, 2)
            First dimension describes different vertices, second dimension x and y coordinates
        :return:
        """
        # TODO: If not numpy array need to loop to set
        self.vertex_pos = positions
        self._update_view()

    def set_weights(self, weights):
        """

        :param weights: Numpy 2D array
            2D weight matrix
        :return:
        """
        self.edge_weights = weights
        self._update_view()

    # might not be needed
    def set_vertex_ids(self, vertex_ids):
        """
        Sets the IDs for all vertices
        :param vertex_ids: List or numpy 1D array
            One-dimensional list of IDs of vertices (e.g. electrode number)
        :return: void
        """
        self.vertex_ids = vertex_ids
        self.vertex_id_to_index = {id: index for id, index in enumerate(self.vertex_ids)}
        self.vertex_index_to_id = {index: id for id, index in enumerate(self.vertex_ids)}
        self._update_view()

    def set_edges(self, edges):
        # TODO: Check if needs to be done together with weights
        self.edges = edges
        self._update_view()

    def get_weights(self):
        return self.edge_weights
