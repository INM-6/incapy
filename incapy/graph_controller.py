
from incapy.load_data import load_data_random
from incapy.icontroller import IController


class GraphAlgorithm(IController):
    def __init__(self, model):
        super().__init__(model)
        load_data_random(model, 10)


