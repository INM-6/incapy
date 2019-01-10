from .imodel import IModel


class GraphModel(IModel):

    def __init__(self):
        super().__init__()
        self.edgeSource = []
        self.edgeTarget = []
        self.edgeWeights = []
        self.node_indices = []
        self.nodeX = []
        self.nodeY = []
        self.listeners = []

    def add_listener(self, view):
        self.listeners.append(view)

    def _update_view(self):
        for l in self.listeners:
            l.update(((self.edgeSource, self.edgeTarget), (self.nodeX, self.nodeY, self.node_indices)))

    def set_positions(self, data):
        # TODO: If not numpy array need to loop
        # data = data.T
        self.nodeX = data[0]
        self.nodeY = data[1]
        self._update_view()

    def set_weights(self, data):
        # TODO: Check data input
        for i, source in enumerate(data):
            for j, target in enumerate(source):
                self.edgeWeights.append(data[i, j])
        self._update_view()

    # might not be needed
    def set_ids(self, data):
        # TODO: Check data input
        self.node_indices = data
        self.edgeSource = []
        self.edgeTarget = []
        # TODO: Check if needs to be done together with weights
        for source in data:
            for target in data:
                self.edgeSource.append(source)
                self.edgeTarget.append(target)
        self._update_view()
