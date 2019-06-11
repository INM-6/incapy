import numpy as np


class FDLayout:

    def __init__(self, model, repulsive_const, anim_speed_const):
        self.model = model
        self.repulsive_const = repulsive_const
        self.anim_speed_const = anim_speed_const
        # Initialize the algorithm by calculating the spring length and the graph center.
        self.natural_spring_length = self.calculate_spring_length()
        self.graph_center = self.calculate_graph_center()

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
        natural_spring_length = 1.5 * sum_edge_lengths/len(self.model.edges.T[0])

        return natural_spring_length

    def calculate_graph_center(self):
        """
        Calculates the graph center.

        :return: None

        """

        # TODO Calculate graph center
        graph_center = (4.5, 4.5)
        return graph_center

    @staticmethod
    def weights_from_corr_linear(weights):
        return weights*(-1)+1

    def __call__(self, max_step_size, *args, **kwargs):
        self.do_step(max_step_size)

    def do_step(self, max_step_size):
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
                                   np.full_like(displacement_length[:, np.newaxis], max_step_size))

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
