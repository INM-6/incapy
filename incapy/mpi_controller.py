from .graph_controller import GraphAlgorithm
from .incapy_interface import start, get_data
from .controller import Controller

import threading
import os
import numpy as np
import time
from mpi4py import MPI


class MPIController(Controller):

    def __init__(self, model, repulsive_const, anim_speed_const, time_per_window, **kwargs):
        """
        Constructor for the GraphAlgorithm class. Initializes all attributes.

        :param model:
            The model class
        :param filename: string
            The filename to the data to be loaded
        :param repulsive_const: float
            repusive constant
        :param anim_speed_const: float
            animation speed constant
        """

        super().__init__(model, repulsive_const=repulsive_const, anim_speed_const=anim_speed_const)

        # Load the data
        # Should be single call to start()
        # TODO should not be needed any more later
        self.metadata = start()

        # Populate the model with the data
        self.populate_model(self.metadata)

        # NOTE: edge_threshold needs to be set before calling update weights
        # TODO should not be needed any more later (once StreamView is created)
        self.current_window = 0

        # The color attributes for the nodes
        self.get_color_attributes()

        # Repeat is by default false, meaning that after the last window, no more windows will be loaded
        self.repeat = False

        # The time (in seconds) when to load the new window
        self.time_per_window = time_per_window

        # # FOR MPI
        self.data_received_event = threading.Event()
        self.data_received_event.clear()

        self.init_algorithm()
        self.data = np.empty((len(self.model.vertex_ids), len(self.model.vertex_ids)))

        # XXX To avoid recursion in set_matrix_from_mpi due to update of view and thus deadlock
        self.next_window_flag = threading.Event()

        # The time (in seconds) when to load the new window
        self.time_per_window = 0.1
        self.current_window_time = 0

    def receive_data(self):
        self.data = get_data()

    def next_window(self, value=None):

        # XXX To avoid recursion and thus deadlock
        if self.next_window_flag.isSet():
            return

        self.receive_data()
        self.set_matrix_from_mpi(self.data)
        self.data_received_event.set()

    def set_matrix_from_mpi(self, data):
        # TODO: Get from MPI
        # self.raw_corr = self.loader.weights[1]*(-1)+1

        # XXX To avoid recursion and thus deadlock
        if self.next_window_flag.is_set():
            return

        self.raw_corr = data
        # TODO: Modularize
        with self.mutex:
            # XXX To avoid recursion and thus deadlock
            self.next_window_flag.set()
            self.model.set_weights(self.weights_from_corr_linear(self.raw_corr), self.current_window)
            # XXX To avoid recursion and thus deadlock
            self.next_window_flag.clear()
            self.set_edge_threshold()

    def run_iteration(self):
        """
        Orchestrating function for running the animation.

        :return: None

        """

        self.next_window()

        # TODO make skip weights based on number of iterations (reproducability)
        self.data_received_event.wait()

        # Time is needed for updating weights after certain time (update_weight_time)
        last_time = time.time()
        self.current_window_time = last_time

        # TODO needs to be changed
        # self.next_window(0)
        self.init_algorithm()

        # TODO: Maybe catch Keyboard interrupt to output position

        while True:
            # Wait for other events
            self.wait_event.wait()
            # If stop is requested,
            if self.stop:
                # stop the run_iteration
                break

            # This makes the speed of the animation constant
            # Even if the framerate drops, vertices will move at about the same speed
            curr_time = time.time()
            dt = curr_time - last_time
            last_time = curr_time

            # dt must be bounded, in case of string lag positions should not jump too far
            dt = min(dt, 0.1)
            self.max_step_size = self.anim_speed_const * dt

            # Load the new window, if the update_weight_time is reached
            if curr_time - self.current_window_time > self.time_per_window:
                if self.time_per_window != 0:
                    self.next_window()
                # Note: Needs to be set so if slider that specifies time per window is moved away from 0,
                # the window will not be switched immediately!!! So time needs to be around 0 at any moment
                # when self.update_weight_time is 0
                self.current_window_time = curr_time

            with self.mutex:
                # The function to calculate the new positions
                self.do_step()
