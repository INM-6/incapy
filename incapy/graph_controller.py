
import threading
from .controller import Controller
import time
import math
import numpy as np


class GraphAlgorithm(Controller):
    """

    The concrete controller. All the calculations are handled here.
    Controls all the transactions and interactions.

    """

    def __init__(self, model, filename, data_loader, repulsive_const, anim_speed_const, time_per_window, **kwargs):
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
        :param data_loader: class
            The dataloader class

        """

        super().__init__(model, repulsive_const=repulsive_const, anim_speed_const=anim_speed_const)

        # Load the data
        self.loader = data_loader()
        self.metadata = self.loader.load_data(filename)

        # Populate the model with the data
        self.populate_model(self.metadata)

        # NOTE: edge_threshold needs to be set before calling update weights
        self.current_window = -1

        # Sets the weights
        self.next_window(0)

        # The color attributes for the nodes
        self.get_color_attributes()

        # Repeat is by default false, meaning that after the last window, no more windows will be loaded
        self.repeat = False

        # The time (in seconds) when to load the new window
        self.time_per_window = time_per_window

    def get_metadata(self):
        return self.loader.load_data(self)

    def set_update_weight_time(self, value):
        """
        Sets the time between the windows to be loaded to 'value' (set via slider by user)

        :param value: int
            Time (in seconds) when to load next window

        :return: None

        """

        # Explicitly NOT reset time that current window has been used
        self.time_per_window = value
        self.model.set_update_weight_time(value)

    def set_repeat(self, value):
        """
        Sets the repeat value.

        :param value: bool
            'True' when repeat is requested, else 'False'

        :return: None

        """

        self.repeat = value

    def populate_model(self, metadata):
        """
        Populates the model with the data from the loader.

        :return: None

        """

        super().populate_model(metadata)
        self.model.set_number_windows(self.metadata['number_windows'])

    def next_window(self, value=None):
        """
        Updates the weights with the current_window weights from the loader.

        :param: value
            The window to be loaded

        :return: None

        """

        # XXX Prevent deadlock due to notification upon change of slider
        if value == self.current_window:
            return
        if value is None:
            self.current_window += 1
            curr_window = self.current_window

        else:
            curr_window = value
            self.current_window = value
        # sends the data to the model and update the matrix every few seconds
        try:
            with self.mutex:
                self.model.set_weights(self.loader.weights[curr_window], curr_window)
                self.set_edge_threshold()
                # New window has now been used for 0 seconds
                # Thus this time needs to be reset in order not to move on too fast
                # If this is not done, this window will be replaced by the next after a too short period of time
                self.current_window_time = time.time()
        except IndexError:
            if self.repeat:
                self.next_window(0)

        # TODO introduce error handling after last iteration of correlations
        # maybe call stop_iteration

    def run_iteration(self):
        """
        Orchestrating function for running the animation.

        :return: None

        """

        # TODO make skip weights based on number of iterations (reproducability)

        # Time is needed for updating weights after certain time (update_weight_time)
        last_time = time.time()
        self.current_window_time = last_time

        self.next_window(0)
        self.init_algorithm()

        # TODO: Maybe catch Keyboard interrupt to output position

        while True:
            # In case of pause wait for continue signal
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
            self.max_step_size = self.anim_speed_const*dt

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
