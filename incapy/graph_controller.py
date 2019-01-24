from .load_data import DataLoader, load_data_debug
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
        self.current_frame = 0
        self.update_weights()
        self.natural_spring_length = None
        self.graph_center = None
        self.repulsive_const = 0.115
        self.anim_speed_const = 1
        self.max_step_size = 0.01

    def populate_model(self):
        # set attributes of the graph
        # TODO graph needs to know weights(cross_correlation) and edge_ids
        self.model.set_vertex_ids(self.loader.vertex_ids)
        self.model.set_positions(self.loader.positions[:, 1:3].T)
        self.model.set_edges(self.loader.edge_ids)
        # load_data_debug(self.model)

    def calculate_weights(self):
        # calculate actual weights from x_corr
        # TODO Use Sigmoid function
        self.loader.weights = np.abs(self.loader.x_corr[1:] - 1)

    def update_weights(self):
        # sends the data to the model and update the matrix every few seconds
        self.model.set_weights(self.loader.weights[self.current_frame])
        self.current_frame += 1
        # self.model.set_weights([1, 0.5, 0])

    def start_iteration(self):
        count = 0
        self.update_weights()
        self.init_algorithm()
        # TODO: Maybe catch Keyboard interrupt to output position
        while True:
            if not count%100:
                #print(count)
                if not count % 100:
                    self.update_weights()
            count += 1
            # time.sleep(1)
            self.do_step()
            try:
                pass
                # self.update_weights()
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

    # Numpy mashgrid
    # Broadcasting
    def do_step(self):
        # TODO: Check if copy is needed???
        # next_positions = self.model.vertex_pos.copy()
        source_pos = self.model.vertex_pos[:, np.newaxis, :]
        print(source_pos.shape)
        target_pos = self.model.vertex_pos[np.newaxis, :, :]
        diff = target_pos - source_pos
        print(diff.shape)
        diff_length = diff[:, :, :]
        diff_length = diff_length**2
        diff_length = np.sqrt(np.sum(diff_length, axis=-1))
        diff_length[diff_length == 0] = 1
        diff = diff/diff_length[:, :, np.newaxis]
        displacement = diff*self.repulsive_const*(self.natural_spring_length**2)
        displacement *= self.model.edge_weights[:, :, np.newaxis]
        # TODO: Add weights, attraction
        spring_force = diff_length ** 2 / self.natural_spring_length
        displacement -= diff*spring_force[:, :, np.newaxis]

        displacement = np.sum(diff, axis=-2)

        # Make sure length of displacement fits
        displacement_length = displacement**2
        displacement_length = np.sqrt(np.sum(displacement_length, axis=-1))
        displacement = displacement/displacement_length[:, np.newaxis]
        displacement *= np.minimum(displacement, np.full_like(displacement, self.max_step_size))

        self.model.vertex_pos+=displacement

        # Axis 0 or 1 indexed? FIRST AXIS!!!
        diff_to_center = np.sum(self.model.vertex_pos, axis=-2)
        diff_to_center /= len(self.model.vertex_indices)
        diff_to_center -= self.graph_center

        self.model.vertex_pos = self.model.vertex_pos - diff_to_center[np.newaxis, :] * self.anim_speed_const

        # for source in self.model.vertex_indices:
        #     source_pos =  np.full(())
        #     displacement = np.array((0, 0), dtype='float64')
        #     for target in self.model.vertex_indices:
        #         # Need to check every edge for every single node (even if 1-2 was already used for 1, it needs to be used for 2 as well!!!!)
        #         if source != target:
        #             # Edges are saved such that source < target => Index in different way
        #             edgesource = min(source, target)
        #             edgetarget = max(source, target)
        #             source_pos = self.model.vertex_pos[source]
        #             target_pos = self.model.vertex_pos[target]
        #             diff = target_pos - source_pos
        #             diff_length = self._vector_length(diff)
        #             diff = diff / diff_length
        #             # Calculate the repulsive force
        #             # Unique id of edge
        #             edge_id = (len(self.model.vertex_indices)+1)*edgesource+edgetarget
        #             edge_index = self.model.edge_indices[edge_id]
        #             weight = self.model.edge_weights[edge_index]
        #             # print(diff, weight)
        #
        #             repulsive_force = self.repulsive_const * self.natural_spring_length * self.natural_spring_length
        #             # Repulsive force moves them away from each other
        #             displacement -= diff * repulsive_force * weight
        #             # calculate attractive forces
        #             # TODO: only calculate with neighbours (maybe need own for loop)
        #             spring_force = diff_length**2/self.natural_spring_length
        #             # Spring force moves them towards each other
        #             displacement += diff * spring_force
            # Force all vertices towards center
        #     displacement_length = self._vector_length(displacement)
        #     displacement = displacement / displacement_length
        #     displacement *= min(displacement_length, self.max_step_size)
        #     # TODO: Inform model of change
        #     self.model.vertex_pos[source] += displacement
        # # Force to center of graph
        # diff_to_center = np.array((0, 0), dtype='float64')
        # for source in self.model.vertex_indices:
        #     diff_to_center += self.model.vertex_pos[source]
        # diff_to_center = diff_to_center/len(self.model.vertex_indices)-self.graph_center
        # for source in self.model.vertex_indices:
        #     self.model.vertex_pos[source] -= diff_to_center * self.anim_speed_const
        # # TODO: DO NOT ACCESS PRIVATE MEMBERS IN OTHER CLASSES
        self.model._update_view()
        #self.model.set_positions(next_positions.T)
