from .imodel import IModel
import numpy as np

class GraphModel(IModel):

    def __init__(self):
        super().__init__()
        self.edge_source = []
        self.edge_target = []
        self.edge_weights = []
        self.vertex_indices = []
        self.vertex_pos = []
        self.listeners = []
        self.edge_indices = {}

    def add_listener(self, view):
        self.listeners.append(view)

    def _update_view(self):
        for l in self.listeners:
            l.update(((self.edge_source, self.edge_target), (np.array(self.vertex_pos), self.vertex_indices)))

    def set_positions(self, data):
        # TODO: If not numpy array need to loop
        # data = data.T
        self.vertex_pos = data.T
        self._update_view()

    def set_weights(self, data):
        # TODO: Check data input
#<<<<<<< Updated upstream
        self.edge_weights = data
        print(self.edge_weights)
# =======
#         # TODO set_ids must be called before calling set_weights
#         counter = 0
#         self.edgeWeights = np.ndarray((len(self.node_indices)*(len(self.node_indices)+1)//2,))
#         # TODO: Check if numpy can do this better
#         for i, source in enumerate(data):
#             for j, target in enumerate(source):
#                 self.edgeWeights[counter] = data[i, j]
#                 counter += 1
# >>>>>>> Stashed changes
        self._update_view()


    # might not be needed
    def set_vertex_ids(self, data):
        # TODO: Check data input
#<<<<<<< Updated upstream
        self.vertex_indices = data
# =======
#         counter = 0
#         self.node_indices = data
#         print(self.node_indices)
#         self.edgeSource = np.ndarray((len(self.node_indices)*(len(self.node_indices)+1)//2,))
#         self.edgeTarget = np.ndarray((len(self.node_indices)*(len(self.node_indices)+1)//2,))
#         # TODO: Check if needs to be done together with weights
#         # TODO: Check if numpy can do this better
#         for source in data:
#             for target in data:
#                 self.edgeSource[counter]=source
#                 self.edgeTarget[counter]=target
#                 counter += 1
# >>>>>>> Stashed changes
        self._update_view()

    def set_edges(self, data):
        # TODO: Check if needs to be done together with weights
        self.edge_source = data[0]
        self.edge_target = data[1]
        # TODO: better way to access the edges when source and target are known? maybe use matrix (problem missing vertex)
        # TODO: requires set_vertex_ids to be called before, either make sure this happens or reorganise
        self.edge_indices = {data[0][i]*(len(self.vertex_indices)+1) + data[1][i]: i for i in range(len(data[0]))}


    def get_weights(self):
        return self.edge_weights
