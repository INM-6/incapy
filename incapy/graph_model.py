from .imodel import IModel
import numpy as np


class GraphModel(IModel):
    """

    The concrete model containing all the relevant data.

    """

    def __init__(self):
        """
        Constructor for the GraphModel. Initializes all the attributes needed.

        """

        super().__init__()

        self.hex_colors = None
        self.edges = np.ndarray((0, 2))

        # mapping from vertex_indices to matrix_indices!! (e.g. missing node)
        self.edge_weights = []

        self.vertex_ids = []
        self.vertex_pos = []
        self.listeners = []

        # Mapping from internal array indices to external IDs
        self.vertex_id_to_index = {}
        self.vertex_index_to_id = {}
        self.animation_speed = 1
        self.time_to_update_weights = 5
        self.repeat = False

        # Will be filled as boolean array indicating which edges surpass the threshold
        self.edge_threshold_mask = []

    def add_listener(self, view):
        """
        Adds the view to the list of listeners.

        :param view:
            The view to be appended to the listener.

        :return: None

        """

        self.listeners.append(view)

    def _update_view(self):
        """
        Updates all the views.

        :return: None

        """
        try:
            edge_sources = np.compress(self.edge_threshold_mask, self.edges, axis=0).T[0]
            edge_targets = np.compress(self.edge_threshold_mask, self.edges, axis=0).T[1]
        # If any(self.edge_threshold_mask) is False, indexing an empty array is impossible
        except IndexError:
            edge_sources = []
            edge_targets = []
        for l in self.listeners:
            l.update(((edge_sources, edge_targets),
                      (np.array(self.vertex_pos), self.vertex_ids)))

    def set_colors(self, colors):
        self.hex_colors = colors
        for l in self.listeners:
            l.set_colors(self.hex_colors)

    def set_positions(self, positions):
        """
        Sets the vertex positions.

        :param positions: Numpy 2D array, shape (X, 2)
            First dimension describes different vertices, second dimension x and y coordinates
        :return: None

        """

        # TODO: If not numpy array need to loop to set
        self.vertex_pos = positions
        self._update_view()

    def update_ui_elements(self, msg, value=None):
        for l in self.listeners:
            l.update_ui(msg, value)

    def set_weights(self, weights, window):
        """
        Sets the weights.

        :param weights: Numpy 2D array
            2D weight matrix
        :return: None

        """

        self.edge_weights = weights
        self.update_ui_elements("window_change", window)
        #self._update_view()

    # might not be needed
    def set_vertex_ids(self, vertex_ids):
        """
        Sets the IDs for all vertices.

        :param vertex_ids: List or numpy 1D array
            One-dimensional list of IDs of vertices (e.g. electrode number)
        :return: None

        """

        self.vertex_ids = vertex_ids

        # Mapping from vertex_id to index
        self.vertex_id_to_index = {id: index for id, index in enumerate(self.vertex_ids)}

        # Mapping from index to the vertex_id
        self.vertex_index_to_id = {index: id for id, index in enumerate(self.vertex_ids)}

        self._update_view()

    def set_edges(self, edges):
        """
        Sets the edges.

        :param edges: List or numpz 2D array
            An array consisting of pairs of (source, target) that represent edges
        :return: None

        """

        # TODO: Check if needs to be done together with weights
        self.edges = edges
        self._update_view()

    def get_weights(self):
        """
        Returns the weights

        :return: Numpy 2D array
            The edge weights

        """

        return self.edge_weights


    def set_time_weight_update(self, time_to_update_weights):
        print(time_to_update_weights)
        self.time_to_update_weights = time_to_update_weights

    def set_animation_speed(self, animation_speed):
        self.animation_speed = animation_speed

    def get_time_weight_update(self):
        return self.time_to_update_weights

    def get_animation_speed(self):
        return self.animation_speed

    def set_repeat(self, value):
        self.repeat = value

    def get_repeat(self):
        return self.repeat

    def set_edge_threshold_mask(self, mask):
        self.edge_threshold_mask = mask
