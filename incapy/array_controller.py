from .incapy_interface import start, get_data
from .controller import Controller

import threading
import numpy as np


class ArrayController(Controller):

    changeable_values = ("time_per_window",)

    def __init__(self, model, view, data, repulsive_const, anim_speed_const, time_per_window, **kwargs):
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

        self.all_data = data

        super().__init__(model, view, repulsive_const=repulsive_const, anim_speed_const=anim_speed_const,
                                                                time_per_window=time_per_window, **kwargs)

        # XXX To avoid recursion in set_matrix_from_mpi due to update of view and thus deadlock
        self.next_window_flag = threading.Event()

        self.data_index = 0

    def get_metadata(self):
        return self.all_data['metadata']

    def next_window(self, value=None):

        # XXX To avoid recursion and thus deadlock
        if self.next_window_flag.isSet():
            return

        self.receive_data()
        self.set_data(self.data)

    def receive_data(self):
        self.data_index += 1
        self.data_index %= len(self.all_data['data'])
        self.data = self.all_data['data'][self.data_index]

    def set_data(self, data):
        # XXX To avoid recursion and thus deadlock (or endless recursion)
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