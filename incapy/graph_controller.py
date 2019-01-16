from .load_data import DataLoader
from .icontroller import IController
import time


class GraphAlgorithm(IController):

    def __init__(self, model, filename):
        super().__init__(model)
        self.model = model
        self.loader = DataLoader()
        self.loader.load_data(filename)
        self.populate_model()
        self.current_frame = 1
        self.update_weights()

    def populate_model(self):
        # set attributes of the graph
        # TODO graph needs to know weights(cross_correlation) and edge_ids
        self.model.set_vertex_ids(self.loader.vertex_ids)
        self.model.set_positions(self.loader.positions[:, 1:3].T)
        self.model.set_edges(self.loader.edge_ids)

    def update_weights(self):
        # TODO calculate weights from correlation beforehand (1-correlation)
        # sends the data to the model and update the matrix every few seconds
        self.model.set_weights(self.loader.x_corr[self.current_frame])
        self.current_frame += 1

    def start_iteration(self):
        while True:
            time.sleep(1)
            try:
                self.update_weights()
            except IndexError:
                break
            # TODO introduce error handling after last iteration of correlations
            # maybe call stop_iteration

    def stop_iteration(self):
        raise NotImplementedError

    def _iterate(self):
        # calculations for one time step
        raise NotImplementedError()
