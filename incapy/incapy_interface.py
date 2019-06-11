import numpy as np
from .load_data import DataLoader

def start():
    num_vert = 100
    vertex_ids = np.arange(0, num_vert, 1)
    edge_ids = np.arange(num_vert*(num_vert-1)/2)
    edge_ids = np.empty((5050, 2), dtype=np.int32)
    import itertools as it
    edge_ids = np.array(list(it.combinations(vertex_ids, 2)))
    positions = np.array(np.meshgrid(np.arange(10), np.arange(10)))
    arr = np.ndarray((100, 2))
    arr[:, 0] = np.hstack(positions[0])
    arr[:, 1] = np.hstack(positions[1])
    positions = arr
    res = {'positions': positions,
           'vertex_ids': vertex_ids,
           'edge_ids': edge_ids,
           'number_windows': 0}
    return res


def get_data():
    global i
    i += 1
    i %= 5
    res = data[i]
    return res

global i
i = 0
loader = DataLoader()
loader.load_data('/home/mueller/Projekte/INCAPY/data/corr_data.h5')

data = np.empty((500, 100, 100))
data = np.random.rand(*data.shape)
data = loader.weights
