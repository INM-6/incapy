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
        # TODO: Should be changeable by user
        self.repulsive_const = 1  # Daniel: 1
        self.anim_speed_const = 1
        # 1/20 is replacement for time since last frame (i.e. frame rate would be 20Hz)
        self.max_step_size = self.anim_speed_const/20   # Daniel: 0.9, is however changed every step

    def populate_model(self):
        # set attributes of the graph
        # TODO graph needs to know weights(cross_correlation) and edge_ids
        self.model.set_edges(self.loader.edge_ids)
        self.model.set_vertex_ids(self.loader.vertex_ids)
        self.model.set_positions(self.loader.positions[:, 1:3])

    def calculate_weights(self):
        # calculate actual weights from x_corr
        # TODO Use Sigmoid function
        pass

    def update_weights(self):
        # sends the data to the model and update the matrix every few seconds
        self.model.set_weights(self.loader.weights[self.current_frame])
        self.current_frame += 1
        #self.model.set_weights([1, 1, 0.5, 1, 0, 1])

    def start_iteration(self):
        count = 0
        last_time = time.time()
        self.update_weights()
        self.init_algorithm()
        # TODO: Maybe catch Keyboard interrupt to output position
        while True:
            if not count%100:
                print(count)
                if not count % 300:
                    print("Weights updated")
                    self.update_weights()
            count += 1
            # This makes the speed of the animation constant
            # Even if the framerate drops, vertices will move at about the same speed
            curr_time = time.time()
            dt = curr_time - last_time
            last_time = curr_time
            # dt must be bounded, in case of string lag positions should not jump too far
            dt = min(dt, 0.1)
            self.max_step_size = self.anim_speed_const*dt
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
        for nodes in self.model.edges:
            vector_0 = self.model.vertex_pos[nodes[0]]
            vector_1 = self.model.vertex_pos[nodes[1]]
            sum_edge_lengths += self._vector_length(vector_0-vector_1)
        self.natural_spring_length = 1.5 * sum_edge_lengths/len(self.model.edges.T[0])


    def calculate_graph_center(self):
        # TODO Calculate graph center
        self.graph_center = (5, 5)

    # Numpy mashgrid
    # Broadcasting
    def do_step(self):
        # TODO: Check if copy is needed???

        # Get all positions twice: for target and source; reshape so they can be broadcast together by numpy
        source_pos = self.model.vertex_pos[:, np.newaxis, :]
        target_pos = self.model.vertex_pos[np.newaxis, :, :]
        # Creates matrix NxNx2 where n is number of vertices; diff[0][1] is difference vector between vertices 0 and 1
        diff = source_pos - target_pos
        # Create copy in order to calculate lengths from that
        # Copy will be heavily changed
        diff_length = diff[:, :, :]

        # Length of vector is sqrt of sum of squares of coordinates
        # square
        diff_length = diff_length**2
        # sum and sqrt
        diff_length = np.sqrt(np.sum(diff_length, axis=-1))
        # Avoid division of 0/0
        diff_length[diff_length == 0] = 1
        # Normalize all difference vectors
        diff = diff/diff_length[:, :, np.newaxis]

        # Calculate repulsive forces
        # Repulsion vector as a function of difference vector and edge weights
        displacement = diff*self.repulsive_const*(self.natural_spring_length**2)/diff_length[:, :, np.newaxis]
        displacement *= self.model.edge_weights[:, :, np.newaxis]

        # Calculate attractive forces
        # Attraction vector as function of distance
        # TODO: Only calculate if the vertices are indeed adjacent,
        # TODO: currently always the case, else need to set weight 0 or something
        spring_force = diff_length ** 2 / self.natural_spring_length
        displacement -= diff*spring_force[:, :, np.newaxis]

        # Displacement was calculated for each pair of vectors
        # Now need to sum over all target vertices for all source vertices
        displacement = np.sum(displacement, axis=-2)

        # Make sure length of displacement fits
        # Own matrix for length calculations analogous to diff
        displacement_length = displacement**2
        displacement_length = np.sqrt(np.sum(displacement_length, axis=-1))

        # Normalize displacements
        displacement = displacement/displacement_length[:, np.newaxis]

        # Displacements are capped at certain length
        # If their length is less than max_step_size, nothing changes, otherwise their length will be max_step_size
        displacement *= np.minimum(displacement_length[:, np.newaxis],
                                   np.full_like(displacement_length[:, np.newaxis], self.max_step_size))

        # Now update model with displacment vectors per source vertex
        self.model.vertex_pos += displacement

        # Force everything around a common center
        # Sum all positions
        # Axis 0 or 1 indexed? FIRST AXIS!!!
        diff_to_center = np.sum(self.model.vertex_pos, axis=-2)
        # Average of all positions is 'middle' of graph
        diff_to_center /= len(self.model.vertex_ids)
        # Difference of middle of graph to predefined center
        diff_to_center -= self.graph_center

        # Move all towards center such that 'middle' of graph eventually becomes equal to center
        # anim_speed_const needs to be bounded here because else the vertices will overshoot the center
        self.model.vertex_pos = self.model.vertex_pos - diff_to_center[np.newaxis, :] * min(self.anim_speed_const, 1)

        # # TODO: Inform model of change
        # # TODO: DO NOT ACCESS PRIVATE MEMBERS IN OTHER CLASSES
        self.model._update_view()
        # self.model.set_positions(next_positions.T)
