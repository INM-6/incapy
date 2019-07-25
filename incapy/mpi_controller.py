from .incapy_interface import start, get_data
from .controller import Controller

import threading
import numpy as np


class MPIController(Controller):

    changeable_values = ("time_per_window",)

    def __init__(self, model, view, repulsive_const, anim_speed_const, time_per_window, **kwargs):
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

        # Not passing time_per_window, thus keeping it 0
        super().__init__(model, view, repulsive_const=repulsive_const, anim_speed_const=anim_speed_const,
                                                                time_per_window=time_per_window, **kwargs)

        self._time_per_window = 0.01

    def get_metadata(self):
        return start()

    def next_window(self, value=None):

        # XXX To avoid recursion and thus deadlock
        if self.next_window_flag.isSet():
            return

        self.receive_data()
        self.set_data(self.data)

    def receive_data(self):
        self.data = get_data()
