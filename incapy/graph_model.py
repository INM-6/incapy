from .imodel import IModel


class GraphModel(IModel):

    def __init__(self):
        super().__init__()
        self.edge_source = []
        self.edge_target = []
        self.edge_weights = []
        self.vertex_indices = []
        self.vertex_x = []
        self.vertex_y = []
        self.listeners = []

    def add_listener(self, view):
        self.listeners.append(view)

    def _update_view(self):
        for l in self.listeners:
            l.update(((self.edge_source, self.edge_target), (self.vertex_x, self.vertex_y, self.vertex_indices)))

    def set_positions(self, data):
        # TODO: If not numpy array need to loop
        # data = data.T
        self.vertex_x = data[0]
        self.vertex_y = data[1]
        self._update_view()

    def set_weights(self, data):
        # TODO: Check data input
        self.edge_weights = data
        print(self.edge_weights)
        self._update_view()

    # might not be needed
    def set_vertex_ids(self, data):
        # TODO: Check data input
        self.vertex_indices = data
        self._update_view()

    def set_edges(self, data):
        # TODO: Check if needs to be done together with weights
        self.edge_source = data[0]
        self.edge_target = data[1]

    def get_weights(self):
        return self.edge_weights
