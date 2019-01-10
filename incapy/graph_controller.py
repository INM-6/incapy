from .load_data import load_data_random
from .icontroller import IController
import time


class GraphAlgorithm(IController):

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        load_data_random(model, 10)

    def set_matrix(self):
        # sends the data to the model and update the matrix every few seconds
        raise NotImplementedError()

    def start_iteration(self):
        while True:
            time.sleep(1)
            load_data_random(self.model, 10)

    def stop_iteration(self):
        raise NotImplementedError

    def _iterate(self):
        # calculations for one time step
        raise NotImplementedError()
