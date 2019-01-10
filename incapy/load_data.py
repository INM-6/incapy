
import numpy as np
import h5py as h5


class DataLoader:

    def __init__(self):
        self.x_corr = None
        self.positions = None
        self.vertex_ids = None

    def load_data(self, model, filename):
        # load the data from the hdf5 files (2-dimensional weighted matrix)
        # and populate the empty graph
        self.load_graph_topology_time_variant(model, filename)

    def load_graph_topology_time_variant(self, model, filename):
        if self.x_corr is None:
            file = h5.File(filename, 'r')
            # Read vertex IDs, i.e. currently 0 to 99
            self.vertex_ids = np.array(file['vertexIDs'])

            # Read edge IDs, i.e. an array consisting of pairs of (source, target) that represent edges
            # TODO currently not used
            edge_ids = np.array(file['edgeIDs'])

            # defines start and stop timestamp for each set of cross-correlations
            # TODO currently not used
            frameDurs = np.array(file['timeVariantData/frameDuration'])

            # TODO: Check if adjacency also needed (static edge attributes)
            # TODO: Check if 'isDirected' is needed

            # Edge Attributes (time variant)
            self.x_corr = np.array(file['timeVariantData/edgeAttributes/CrossCorrelations']).T

            # Vertex Attributes
            self.positions = np.array(file['staticData/vertexAttributes/position'])

        # set attributes of the graph
        # TODO graph needs to know weights(cross_correlation) and edge_ids
        model.set_ids(self.vertex_ids)
        model.set_positions(self.positions[:, 1:3].T)

def load_data_random(model, num_nodes):
    node_indices = np.arange(num_nodes)
    model.set_ids(node_indices)
    positions = np.random.rand(2, num_nodes)
    model.set_positions(positions)

