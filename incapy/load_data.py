from __future__ import absolute_import
#from incapy.graph_model import GraphModel
import numpy as np
import h5py as h5
crosscorr = []
positions = []
vertexIDs = []

def load_data(model, filename):
    # load the data from the hdf5 files (2-dimensional weighted matrix)
    # and populate the empty graph
    load_graph_topology_time_variant(model, filename)
    #raise NotImplementedError()

def load_graph_topology_time_variant(model, filename):
    global crosscorr
    global positions
    global vertexIDs
    if not crosscorr:
        file = h5.File(filename, 'r')
        # Read vertex IDs, i.e. currently 0 to 99
        vertexIDs = np.array(file['vertexIDs'])
        print(vertexIDs)
        # Read edge IDs, i.e. an array consisting of pairs of (source, target) that represent edges
        edgeIDs = np.array(file['edgeIDs'])
        print(edgeIDs)

        frameDurs = np.array(file['timeVariantData/frameDuration'])
        print(frameDurs)

        # TODO: Check if adjacency also needed (static edge attributes)
        # TODO: Check if 'isDirected' is needed

        # Edge Attributes (time variant)
        crosscorr = np.array(file['timeVariantData/edgeAttributes/CrossCorrelations']).T
        print(crosscorr)

        # Vertex Attributes
        positions = np.array(file['staticData/vertexAttributes/position'])
        print(positions)
        print(positions[:, 1:3].T)

    model.set_ids(vertexIDs)
    model.set_positions(positions[:, 1:3].T)

def load_data_random(model, num_nodes):
    node_indices = np.arange(num_nodes)
    model.set_ids(node_indices)
    positions = np.random.rand(2, num_nodes)
    model.set_positions(positions)
    # print(positions)
    # print(model.nodeX)
    # print(model.nodeY)


if __name__ == '__main__':
    load_graph_topology_time_variant(None, '../../data/corr_data.h5')
    print(crosscorr)
