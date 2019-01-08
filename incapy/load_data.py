import numpy as np


def load_data(graph):
    # load the data from the hdf5 files (2-dimensional weighted matrix)
    # and populate the empty graph
    raise NotImplementedError()


def load_data_random(model, num_nodes):
    node_indices = np.arange(num_nodes)
    model.set_ids(node_indices)
    positions = np.random.rand(2, num_nodes)
    model.set_positions(positions)
    # print(positions)
    # print(model.nodeX)
    # print(model.nodeY)
