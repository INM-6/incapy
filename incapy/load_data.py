
import numpy as np
import h5py as h5


class DataLoader:
    """
    Class to load the data from the (hdf5) file.

    """

    def __init__(self):
        """
        Constructor for class DataLoader. Sets all the attributes to None.

        """

        # The correlation between two vertices (only needed for loading the data, then saved in 'self.weights'
        self.x_corr = None

        # Array of starting positions of the vertices
        self.positions = None

        # Vertex IDs
        self.vertex_ids = None

        # An array consisting of pairs of (source, target) that represent edges
        self.edge_ids = None

        # Defines start and stop timestamp for each set of cross-correlations
        self.frame_durations = None

        # Weights is an upper triangular matrix consisting of the weights between the vertices
        self.weights = None

    def load_data(self, filename):
        """
        Loads the data from the hdf5 file. Another loading
        routine can be added.

        :param filename: string
            The filename for the hdf5 file with the data
        :return: None

        """

        self.load_graph_topology_time_variant(filename)

    def load_graph_topology_time_variant(self, filename):
        """
        Loads the data from the hdf5 files and populates the
        empty graph.

        :param filename: string
            The filename for the hdf5 file with the data
        :return: None

        """

        # The filename, reading mode only
        file = h5.File(filename, 'r')

        # Read vertex IDs, i.e. currently 0 to 99
        self.vertex_ids = np.array(file['vertexIDs'])

        # Read edge IDs, i.e. an array consisting of pairs of (source, target) that represent edges
        # TODO currently not used
        self.edge_ids = np.array(file['edgeIDs'])

        # Defines start and stop timestamp for each set of cross-correlations
        # TODO currently not used (set manually)
        self.frame_durations = np.array(file['timeVariantData/frameDuration'])

        # TODO: Check if adjacency also needed (static edge attributes)
        # TODO: Check if 'isDirected' is needed

        # Edge Attributes (time variant)
        self.x_corr = np.array(file['timeVariantData/edgeAttributes/CrossCorrelations']).T

        # TODO: Check when missing an index!!!
        # NEED INDICES BEFORE AND EDGES
        num_vert = len(self.vertex_ids)
        self.weights = np.zeros((self.x_corr.shape[0]-1, num_vert, num_vert), dtype='float64')
        upper = np.triu_indices(num_vert)

        # TODO: Optimize using numpy, could remove for loop
        for timestamp in range(self.x_corr.shape[0]-1):

            # Set weights into upper triangular matrix
            self.weights[timestamp][upper] = self.x_corr[1:][timestamp]
            self.weights[timestamp] += self.weights[timestamp].T

            # Numpy magic to subtract added values on diagonal; should not make a difference
            # Because diagonal represents correlation from electrode n to n
            self.weights[timestamp] -= np.diag(np.diag(self.weights[timestamp]))

            # Actually calculate graph weights from xcorr
            # Currently this is 1-xcorr
            self.weights[timestamp], _ = self.x_corr_to_weight(self.weights[timestamp])

        # Vertex Attributes
        self.positions = np.array(file['staticData/vertexAttributes/position'])

    def x_corr_to_weight(self, x_corr):
        # weight = 1-x_corr
        weight = x_corr*(-1)+1
        inverse_sign = True
        return weight, inverse_sign
