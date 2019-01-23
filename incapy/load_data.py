
import numpy as np
import h5py as h5


class DataLoader:

    def __init__(self):
        self.x_corr = None
        self.positions = None
        self.vertex_ids = None
        self.edge_ids = None
        self.frame_durations = None

    def load_data(self, filename):
        # load the data from the hdf5 files (2-dimensional weighted matrix)
        # and populate the empty graph
        self.load_graph_topology_time_variant(filename)

    def load_graph_topology_time_variant(self, filename):
        if self.x_corr is None:
            file = h5.File(filename, 'r')
            # Read vertex IDs, i.e. currently 0 to 99
            self.vertex_ids = np.array(file['vertexIDs'])

            # Read edge IDs, i.e. an array consisting of pairs of (source, target) that represent edges
            # TODO currently not used
            self.edge_ids = np.array(file['edgeIDs']).T

            # defines start and stop timestamp for each set of cross-correlations
            # TODO currently not used
            self.frame_durations = np.array(file['timeVariantData/frameDuration'])

            # TODO: Check if adjacency also needed (static edge attributes)
            # TODO: Check if 'isDirected' is needed

            # Edge Attributes (time variant)
            self.x_corr = np.array(file['timeVariantData/edgeAttributes/CrossCorrelations']).T


            # Vertex Attributes
            self.positions = np.array(file['staticData/vertexAttributes/position'])


# only for testing purposes
# TODO delete when not needed any more
def load_data_random(model, num_nodes):
    node_indices = np.arange(num_nodes)
    model.set_vertex_ids(node_indices)
    positions = np.random.rand(2, num_nodes)
    model.set_positions(positions)

def load_data_debug(model):
    # Need to allow not directly successing series
    vertex_indices = np.array([0,1,2])
    model.set_vertex_ids(vertex_indices)
    positions = np.array([[0, 4, 4], [0, 3, 0]], dtype='float64')
    model.set_positions(positions)
    model.set_edges([[0, 0, 1], [1, 2, 2]])
