import threading
from abc import ABC, abstractmethod

import numpy as np

from.icontroller import IController
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color

class Controller(IController):
    """
    Abstract base class / interface for the controller.

    """

    def __init__(self, model, repulsive_const, anim_speed_const):
        super().__init__(model)
        self.model = model

        # Needed for threading
        self.wait_event = threading.Event()
        self.mutex = threading.Lock()
        self.run_thread = None
        # Flag that is set to stop or pause execution
        self.stop = False
        # self.metadata = self.get_metadata()
        # self.populate_model(self.metadata)
        # Constants needed for the force-directed layout algorithm
        self.natural_spring_length = None
        # TODO: Calculate center
        self.graph_center = None
        # TODO: Should be changeable by user (interactively?)
        self.repulsive_const = repulsive_const  # Daniel: 1
        self.anim_speed_const = anim_speed_const
        # 1/20 is replacement for time since last frame (i.e. frame rate would be 20Hz)
        self.max_step_size = self.anim_speed_const/20   # Daniel: 0.9, is however changed every step
        # The color attributes for the nodes
        self.hex_colors = None
        # Set edge threshold so displaying works
        # Calling it here will result in no edges being drawn
        self.set_edge_threshold(1)

    #@abstractmethod
    def get_metadata(self):
        raise NotImplementedError()

    def populate_model(self, metadata):
        # set attributes of the graph
        # TODO graph needs to know weights(cross_correlation) and edge_ids
        self.model.set_edges(metadata['edge_ids'])
        self.model.set_vertex_ids(metadata['vertex_ids'])
        self.model.set_positions(self.metadata['positions'])

    def set_edge_threshold(self, threshold=None):
        """
         Sets the edge threshold (all edges greater than the threshold are displayed)

         :param threshold: float
             The edge threshold

         :return: None

         """

        # If threshold has been provided,
        if threshold is not None:
            # Use that threshold
            self.edge_threshold = threshold
        # Check directly from given values, without any transformation
        # Can be changed to use transformed weights instead, if it becomes necessary
        # to remove x_corr from memory
        n = len(self.model.vertex_ids)
        try:
            mask = self.raw_corr[np.triu_indices(n)] > self.edge_threshold
        except AttributeError:
            # If raw correlation is not known yet
            mask = np.full(n*(n+1)//2, False, dtype=bool)
        self.model.set_edge_threshold_mask(mask)

    @abstractmethod
    def next_window(self):
        # sends the data to the model and update the matrix every few seconds
        raise NotImplementedError()

    def get_color_attributes(self):
        """
        Calculates the color attributes of the vertices.

        :return: None

        """

        # First, get colors in LAB and then convert to RGB hex colors to pass to the model.
        # TODO better way to calculate number of rows?
        num_rows = 10#math.ceil(math.sqrt(len(self.loader.vertex_ids)))

        # constant
        # 100 here and 36 for l or 128 here and 20 for l
        f_lab_range = 100.0

        colors_lab = np.ndarray((100, 3), dtype=float)
        colors_lab[:, 0] = 36

        pos = self.metadata['positions']

        colors_lab[:, 1:3] = ((2*f_lab_range*pos[:, 0:2])/num_rows) - f_lab_range

        colors_res = []
        # TODO not always 100?
        for i in range(100):
            currcol = colors_lab[i]
            lab = LabColor(currcol[0], currcol[1], currcol[2])
            res = convert_color(lab, sRGBColor)
            colors_res.append(res.get_rgb_hex())

        # Set the colors in the model
        self.model.set_colors(colors_res)

    def set_anim_speed_const(self, value):
        """
        Sets the animation speed constant to 'value' (set via slider by user)

        :param value: float
            A float ranging from 0.1-1 (slider values)

        :return: None

        """

        self.anim_speed_const = value
        self.model.set_speed_constant(value)

    def weights_from_corr_linear(self, weights):
        return weights*(-1)+1

    def reset(self):
        """
        Resets the animation.

        :return: None

        """

        self.populate_model(self.metadata)
        self.current_window = -1
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

    def stop_iteration(self):
        """
        Stops the iteration.

        :return: None

        """
        self.stop = True

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
            sum_edge_lengths += np.linalg.norm(vector_0-vector_1)
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
        Force-directed graph layout algorithm. Calculates the new positions of
        all the vertices and updates the model and the view.

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

        # Now update new_vertex_positions with displacment vectors per source vertex
        new_vertex_pos = self.model.vertex_pos + displacement

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
        new_vertex_pos = new_vertex_pos - diff_to_center[np.newaxis, :] * min(self.anim_speed_const, 1)

        # Set the new vertex positions
        self.model.set_vertex_pos(new_vertex_pos)
