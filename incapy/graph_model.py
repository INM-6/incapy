
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
        self.time_per_window = 5
        self.repeat = False

        # Will be filled as boolean array indicating which edges surpass the threshold
        self.edge_threshold_mask = []

        # The number of windows
        self.number_windows = None

    def add_listener(self, view):
        """
        Adds the view to the list of listeners.

        :param view:
            The view to be appended to the listener.

        :return: None

        """

        self.listeners.append(view)

    def update_ui_elements(self, msg, value=None):
        """
        Updates the ui_elements in the views.

        :param msg: string
            The message to see what element changed
        :param value:
            The changed value in the view.

        :return: None

        """

        for l in self.listeners:
            l.update_ui(msg, value)

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
        """
        Sets the colors in the views.

        :param colors: 'list'
            A list of the color attributes of all the nodes.

        :return: None

        """

        self.hex_colors = colors
        for l in self.listeners:
            l.set_colors(self.hex_colors)

    def set_number_windows(self, number_windows):
        """
        Update the ui to the specified number of windows.

        :param number_windows: int
            The number of windows in the data

        :return: None

        """

        self.update_ui_elements("window_adjust", number_windows)

    def set_speed_constant(self, speed_constant):
        """
        Sets the speed constant and updates the ui.

        :param speed_constant: float
            Value for the speed constant

        :return: None

        """

        self.update_ui_elements("speed_constant", speed_constant)

    def set_time_per_window(self, time):
        """
        Sets time_per_window and updates the ui (slider).

        :param time:
            The time in seconds

        :return: None

        """

        self.update_ui_elements("weight_time", time)

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

    def set_speed_constant(self, value):
        """
        Sets the speed constant and makes sure to update the ui element related to speed_constant.

        :param value: float
            The speed constant

        :return: None

        """

        self.animation_speed = value
        self.update_ui_elements('speed_constant', value)

    def set_weights(self, weights, window=0):
        """
        Sets the weights.

        :param weights: Numpy 2D array
            2D weight matrix
        :return: None

        """

        self.edge_weights = weights
        self.update_ui_elements("window_change", window)

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

    def set_edge_threshold_mask(self, mask):
        """
        Sets the edge threshold mask.

        :param mask: 'numpy-array'
            Mask which marks all the edges that will be displayed
            according to the edge threshold.

        :return: None

        """

        self.edge_threshold_mask = mask
        self._update_view()

    def set_vertex_pos(self, vertex_positions):
        """
        Sets the vertex positions.

        :param vertex_positions: list
            A list consisting of the vertex positions.

        :return: None

        """

        self.vertex_pos = vertex_positions
        self._update_view()
