from .incapy_interface import start, get_data
from .controller import Controller

import threading
import numpy as np


class MPIController(Controller):

    def __init__(self, model, repulsive_const, anim_speed_const, time_per_window, **kwargs):
        """
        Constructor for the FileController class. Initializes all attributes.

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

        # The time (in seconds) when to load the new window
        self.time_per_window = time_per_window

        # XXX To avoid recursion in set_matrix_from_mpi due to update of view and thus deadlock
        self.next_window_flag = threading.Event()

        # The time (in seconds) when to load the new window
        self.time_per_window = 0.1
        self.current_window_time = 0

    def get_metadata(self):
        return start()

    def next_window(self, value=None):

        # XXX To avoid recursion and thus deadlock
        if self.next_window_flag.isSet():
            return

        self.receive_data()
        self.set_matrix_from_mpi(self.data)

    def receive_data(self):
        self.data = get_data()

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
            self.model.set_weights(self.algorithm.weights_from_corr_linear(self.raw_corr))
            # XXX To avoid recursion and thus deadlock
            self.next_window_flag.clear()
            self.set_edge_threshold()
