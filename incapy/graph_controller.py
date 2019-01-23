from .load_data import DataLoader
from .icontroller import IController
import time
import math
import numpy as np


class GraphAlgorithm(IController):

    def __init__(self, model, filename):
        super().__init__(model)
        self.model = model
        self.loader = DataLoader()
        self.loader.load_data(filename)
        self.calculate_weights()
        self.populate_model()
        self.current_frame = 1
        self.update_weights()
        self.natural_spring_length = None
        self.graph_center = None
        self.repulsive_const = 1
        self.anim_speed_const = 1
        self.max_step_size = 0.5

    def populate_model(self):
        # set attributes of the graph
        # TODO graph needs to know weights(cross_correlation) and edge_ids
        self.model.set_vertex_ids(self.loader.vertex_ids)
        self.model.set_positions(self.loader.positions[:, 1:3].T)
        self.model.set_edges(self.loader.edge_ids)

    def calculate_weights(self):
        # calculate actual weights from x_corr
        # TODO Use Sigmoid function
        self.loader.weights = np.abs(self.loader.x_corr - 1)

    def update_weights(self):
        # sends the data to the model and update the matrix every few seconds
        self.model.set_weights(self.loader.weights[self.current_frame])
        self.current_frame += 1

    def start_iteration(self):
        self.init_algorithm()
        # TODO: Maybe catch Keyboard interrupt to output position
        while True:
            time.sleep(1)
            self.do_step()
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

    # TODO use of np array with only two elements?
    def _vector_length(self, vector):
        return math.sqrt(vector[0]**2+vector[1]**2)

    def init_algorithm(self):
        self.calculate_spring_length()
        self.calculate_graph_center()

    def calculate_spring_length(self):
        # Calculate sum of edge lengths
        sum_edge_lengths = 0
        for nodes in np.vstack((self.model.edge_source,self.model.edge_target)).T:
            vector_0 = self.model.vertex_pos[nodes[0]]
            vector_1 = self.model.vertex_pos[nodes[1]]
            sum_edge_lengths += self._vector_length(vector_0-vector_1)
        self.natural_spring_length = 1.5 * sum_edge_lengths/len(self.model.edge_source)


    def calculate_graph_center(self):
        # TODO Calculate graph center
        self.graph_center = (5, 5)

    def do_step(self):
        for source in self.model.vertex_indices:
            displacement = np.array((0, 0), dtype='float64')
            for target in self.model.vertex_indices:
                if source < target:
                    source_pos = self.model.vertex_pos[source]
                    target_pos = self.model.vertex_pos[target]
                    diff = target_pos - source_pos
                    diff_length = self._vector_length(diff)
                    diff = diff / diff_length
                    # Calculate the repulsive force
                    tmp = self.model.edge_indices[(len(self.model.vertex_indices)+1)*source+target]
                    weight = self.model.edge_weights[tmp]
                    print(diff,weight)

                    repulsive_force = self.repulsive_const * self.natural_spring_length * self.natural_spring_length
                    displacement += diff * repulsive_force * weight
                    # calculate attractive forces
                    # TODO: only calculate with neighbours (maybe need own for loop)
                    spring_force = -diff_length**2/self.natural_spring_length
                    displacement += diff * spring_force
            displacement_length = self._vector_length(displacement)
            displacement = displacement / displacement_length
            displacement *= min(displacement_length, self.max_step_size)
            # TODO: Inform model of change
            self.model.vertex_pos[source] += displacement
        # Force to center of graph
        diff_to_center = np.array((0, 0), dtype='float64')
        for source in self.model.vertex_indices:
            diff_to_center += self.model.vertex_pos[source]
        diff_to_center = diff_to_center/len(self.model.vertex_indices)-self.graph_center
        for source in self.model.vertex_indices:
            self.model.vertex_pos[source]-= diff_to_center * self.anim_speed_const
        # TODO: DO NOT ACCESS PRIVATE MEMBERS IN OTHER CLASSES
        self.model._update_view()