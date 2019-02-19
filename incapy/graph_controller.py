import threading
from .load_data import DataLoader
from .icontroller import IController
import time
import math
import numpy as np


class GraphAlgorithm(IController):
    """

    The concrete controller. All the calculations are handled here.
    Controls all the transactions and interactions.

    """

    def __init__(self, model, filename,repulsive_const, anim_speed_const, update_weight_time):
        """
        Constructor for the GraphAlgorithm class. Initalizes all attributes.

        :param model:
            The model class
        :param filename: string
            The filename to the data to be loaded
        :param repulsive_const: float
            repusive constant
        :param anim_speed_const: float
            animation speed constant


        """

        super().__init__(model)
        self.wait_event = threading.Event()
        self.mutex = threading.Lock()
        self.run_thread = None

        # Flags that are set to stop or pause execution
        self.stop = False
        self.model = model
        self.loader = DataLoader()
        self.loader.load_data(filename)
        self.current_frame = 0
        self.calculate_weights()
        self.populate_model()

        self.current_frame = -1

        # Default value for threshold that determines which edges should be shown
        self.edge_threshold = 0.6
        self.set_edge_threshold(self.edge_threshold)

        self.update_weights()
        self.natural_spring_length = None
        # TODO: Calculate center
        self.graph_center = None
        # TODO: Should be changeable by user
        self.repulsive_const = repulsive_const  # Daniel: 1
        self.anim_speed_const = anim_speed_const
        # 1/20 is replacement for time since last frame (i.e. frame rate would be 20Hz)
        self.max_step_size = self.anim_speed_const/20   # Daniel: 0.9, is however changed every step
        # Get default from file or incapy constructor

        self.repeat = False

        self.update_weight_time = update_weight_time

    def set_edge_threshold(self, threshold=None):
        if threshold is not None:
            self.edge_threshold = threshold
        # 1-threshold is conversion function from xcorr to weight
        # Implemented in DataLoader
        try:
            weight_threshold, inverse_sign = self.loader.x_corr_to_weight(self.edge_threshold)
            # x_corr is supposed to be lower than given threshold
            # Thus, if sign of threshold is inverted, comparison needs to be inverted as well
            if inverse_sign:
                mask = self.loader.x_corr[self.current_frame + 1] > weight_threshold
            else:
                mask = self.loader.x_corr[self.current_frame + 1] < weight_threshold
            self.model.set_edge_threshold_mask(mask)
        # Nothing to do after last weight matrix reached
        # TODO: Implement stop or loop behavior after last matrix
        except IndexError:
            pass


    def set_anim_speed_const(self, value):
        """
        Sets the animation speed constant to 'value' (set via slider by user)

        :param value: float
            A float ranging from 0.1-1 (slider values)

        :return: None

        """

        self.anim_speed_const = value

    def set_update_weight_time(self, value):
        self.update_weight_time = value
        # TODO doing it twice??
        self.model.set_time_weight_update(value)

    def set_repeat(self, value):
        self.repeat = value

    def populate_model(self):
        """
        Populates the model with the data from the loader.

        :return: None

        """

        # set attributes of the graph
        # TODO graph needs to know weights(cross_correlation) and edge_ids
        self.model.set_edges(self.loader.edge_ids)
        self.model.set_vertex_ids(self.loader.vertex_ids)
        self.model.set_positions(self.loader.positions[:, 1:3])

    def calculate_weights(self):
        # calculate actual weights from x_corr
        # TODO Use Sigmoid function
        pass

    def update_weights(self, value=None):
        """
        Updates the weights with the current_frame weights from the loader.

        :return: None

        """
        # XXX Prevent deadlock due to notification upon change of slider
        if value == self.current_frame:
            return
        if value is None:
            self.current_frame += 1
            curr_window = self.current_frame

        else:
            curr_window = value
            self.current_frame = value
        # sends the data to the model and update the matrix every few seconds
        try:
            with self.mutex:
                self.model.set_weights(self.loader.weights[curr_window], curr_window)
                self.set_edge_threshold()
        except IndexError:
            if self.repeat:
                self.update_weights(0)

        # TODO introduce error handling after last iteration of correlations
        # maybe call stop_iteration

    def reset(self):
        self.populate_model()
        self.current_frame = 0
        self.wait_event.clear()
        self.stop = False

    def start_iteration(self):
        """
          Starts the iteration to move the nodes accordingly.

          :return: None

        """
        self.wait_event.set()
        self.run_thread = threading.Thread(target=self.run_iteration)
        self.run_thread.start()

    def run_iteration(self):
        # TODO make skip weights based on number of iterations (reproducability)
        last_time = time.time()
        update_time = last_time
        self.update_weights()
        self.init_algorithm()
        # TODO: Maybe catch Keyboard interrupt to output position
        while True:
            self.wait_event.wait()
            if self.stop:
                break

            # This makes the speed of the animation constant
            # Even if the framerate drops, vertices will move at about the same speed
            curr_time = time.time()
            dt = curr_time - last_time
            last_time = curr_time
            # dt must be bounded, in case of string lag positions should not jump too far
            dt = min(dt, 0.1)
            self.max_step_size = self.anim_speed_const*dt
            if curr_time - update_time > self.update_weight_time:
                if self.update_weight_time != 0:
                    self.update_weights()
                update_time = curr_time
            with self.mutex:
                self.do_step()

    def stop_iteration(self):
        """
        Stops the iteration.

        :return: None

        """
        self.stop = True

    def pause_iteration(self):
        self.wait_event.clear()

    def continue_iteration(self):
        self.wait_event.set()


    def _iterate(self):
        """
        Calculations for one time step.

        :return: None

        """

        raise NotImplementedError()

    # TODO use of np array with only two elements?
    def _vector_length(self, vector):
        """
        Returns the lengt of the 'vector'.

        :param vector: list
            A two-dimensional vector
        :return: float
            The length of the vector

        """

        return math.sqrt(vector[0]**2+vector[1]**2)

    def init_algorithm(self):
        """
        Initialize the algorithm by calculating the spring length
        and the graph center.

        :return: None

        """

        self.calculate_spring_length()
        self.calculate_graph_center()

    def calculate_spring_length(self):
        """
        Calculates the natrual spring length

        :return: None

        """

        # Calculate sum of edge lengths
        sum_edge_lengths = 0
        for nodes in self.model.edges:
            vector_0 = self.model.vertex_pos[nodes[0]]
            vector_1 = self.model.vertex_pos[nodes[1]]
            sum_edge_lengths += self._vector_length(vector_0-vector_1)
        self.natural_spring_length = 1.5 * sum_edge_lengths/len(self.model.edges.T[0])

    def calculate_graph_center(self):
        """
        Calculates the graph center.

        :return: None

        """

        # TODO Calculate graph center
        self.graph_center = (4.5, 4.5)

    # Numpy mashgrid
    # Broadcasting
    def do_step(self):
        """
        Force-directed graph layout algorithm. Calculate the new positions of
        all the vertices and update the model and the view.

        :return: None

        """

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
