from .load_data import DataLoader
from .icontroller import IController
import time


class GraphAlgorithm(IController):

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        self.loader = DataLoader()
        self.loader.load_data(model, '../../data/corr_data.h5')

    def set_matrix(self):
        # sends the data to the model and update the matrix every few seconds
        raise NotImplementedError()

    def start_iteration(self):
        while True:
            time.sleep(1)
            self.loader.load_data(self.model, '')

    def stop_iteration(self):
        raise NotImplementedError

    def _iterate(self):
        # calculations for one time step
        raise NotImplementedError()
