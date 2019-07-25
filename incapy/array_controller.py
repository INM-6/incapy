from .incapy_interface import start, get_data
from .controller import Controller

import threading
import time


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


        self._current_window = 0
        self.repeat = False

    def get_metadata(self):
        return self.all_data['metadata']

    def next_window(self, value=None):
        """
        Updates the weights with the current_window weights from the loader.

        :param: value
            The window to be loaded

        :return: None

        """

        # XXX To avoid recursion and thus deadlock
        if self.next_window_flag.isSet():
            return

        if value is None:
            self._current_window += 1
        else:
            self._current_window = value

        try:
            self.set_data(self.all_data['data'][self._current_window], self._current_window)

            # New window has now been used for 0 seconds
            # Thus this time needs to be reset in order not to move on too fast
            # If this is not done, this window will be replaced by the next after a too short period of time
            self.current_window_time = time.time()

        except IndexError:
            if self.repeat:
                self.next_window(0)

        # TODO introduce error handling after last iteration of correlations
        # maybe call stop_iteration


