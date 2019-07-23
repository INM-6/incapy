import numpy as np
from .load_data import DataLoader

def start():
    global num_grid
    global num_vert
    vertex_ids = np.arange(0, num_vert, 1)
    edge_ids = np.arange(num_vert*(num_vert-1)/2)
    edge_ids = np.empty((num_vert*(num_vert+1)//2, 2), dtype=np.int32)
    import itertools as it
    edge_ids = np.array(list(it.combinations_with_replacement(vertex_ids, 2)))
    positions = np.array(np.meshgrid(np.arange(num_grid), np.arange(num_grid))) * 10/num_grid
    arr = np.ndarray((num_vert, 2))
    arr[:, 0] = np.hstack(positions[1])[:num_vert]
    arr[:, 1] = np.hstack(positions[0])[:num_vert]
    positions = arr
    res = {'positions': positions,
           'vertex_ids': vertex_ids,
           'edge_ids': edge_ids,
           'number_windows': 0}
    return res


def get_data():
    global i
    i += 1
    #i %= 300
    res = data[i]
    # res = l[0]
    return res

global i
i = 0

global num_grid
num_grid = 7
global num_vert
num_vert = 37

loader = DataLoader()
loader.load_data('/home/mueller/Projekte/INCAPY/data/corr_data.h5')
#loader.load_data('/home/mueller/Projekte/INCAPY/data/cpp2_time_variant_data.h5')

data = np.empty((500, 100, 100))
data = np.random.rand(*data.shape)
data = loader.weights

l = data.copy()[:, :num_vert, :num_vert]
r = data[1]
data = np.linspace(l[0], l[1], num=2000, endpoint=False)
for i in range(1, 6-1):
    to_stack = np.linspace(l[i], l[i+1], num=200, endpoint=False)
    data = np.concatenate((data, to_stack))
print(data.shape)
