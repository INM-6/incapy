from .icontroller import IController
from .fd_layout import FDLayout

import time

import threading

from abc import abstractmethod

import numpy as np

from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color


class Controller(IController):
    """
    Abstract base class / interface for the controller.

    """
    changeable_values = ()

    def __init__(self, model, view, repulsive_const, anim_speed_const, algorithm=FDLayout):
        super().__init__(model, view)
        self.model = model
        view.add_event_listener(self)

        self.metadata = self.get_metadata()

        # Populate the model with the data
        self.populate_model(self.metadata)

        # The color attributes for the nodes
        self.get_color_attributes()

        self.algorithm_class = algorithm
        self.algorithm = algorithm(self.model, repulsive_const, anim_speed_const)

        # Needed for threading
        self.wait_event = threading.Event()
        self.mutex = threading.Lock()
        self.run_thread = None
        # Flag that is set to stop or pause execution
        self.stop = False

        # Constants needed for the force-directed layout algorithm
        # TODO: Should be changeable by user (interactively?)
        # TODO: Maybe refactor, if other constants are needed
        self.repulsive_const = repulsive_const  # Daniel: 1
        self.anim_speed_const = anim_speed_const
        # The color attributes for the nodes
        self.hex_colors = None
        # Set edge threshold so displaying works
        # Calling it here will result in no edges being drawn
        self.set_edge_threshold(1)

        self.current_window_time = 0

    @abstractmethod
    def get_metadata(self):
        raise NotImplementedError

    def populate_model(self, metadata):
        # set attributes of the graph
        # TODO graph needs to know weights(cross_correlation) and edge_ids
        self.model.set_edges(metadata['edge_ids'])
        self.model.set_vertex_ids(metadata['vertex_ids'])
        self.model.set_positions(self.metadata['positions'])

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
            max_step_size = self.anim_speed_const*dt

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
                self.algorithm.do_step(max_step_size)

    # Called automatically and as reaction to UI interaction
    @abstractmethod
    def next_window(self, value=None):
        # sends the data to the model and update the matrix every few seconds
        raise NotImplementedError()


    #########################################################
    ########### Reactions to UI interaction #################
    #########################################################

    # TODO: Maybe refactor to dictionary
    def notify_event(self, msg):
        """

        :param msg: string
            The message that is sent from the view.

        :param value:
            The value that changed in the view.

        :return: None

        """

        if msg == 'start':
            self.start_iteration()
        elif msg == 'stop':
            self.stop_iteration()
        elif msg == 'pause':
            self.pause_iteration()
        elif msg == 'play':
            self.continue_iteration()
        elif msg == 'next_window':
            self.next_window()
        elif msg == 'reset':
            self.reset()

        self.algorithm.notify_event(msg)

    def value_changed(self, **kwargs):
        for key in kwargs:
            if key in self.changeable_values:
                setattr(self, key, kwargs[key])
        self.algorithm.value_changed(**kwargs)

    def reset(self):
        """
        Resets the animation.

        :return: None

        """

        self.populate_model(self.metadata)
        self.current_window = -1
        self.wait_event.clear()
        self.stop = False

    def set_time_per_window(self, value):
        """
        Sets the time between the windows to be loaded to 'value' (set via slider by user)

        :param value: int
            Time (in seconds) when to load next window

        :return: None

        """

        # Explicitly NOT reset time that current window has been used
        self.time_per_window = value
        self.model.set_time_per_window(value)

    def set_anim_speed_const(self, value):
        """
        Sets the animation speed constant to 'value' (set via slider by user)

        :param value: float
            A float ranging from 0.1-1 (slider values)

        :return: None

        """

        self.anim_speed_const = value
        self.model.set_speed_constant(value)

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

    def pause_iteration(self):
        """
        Pauses the iteration.

        :return: None

        """

        self.wait_event.clear()

    def continue_iteration(self):
        """
        Continues the iteration after pausing it.

        :return: None
        """

        self.wait_event.set()

    time_per_window = property(lambda self: self.time_per_window, set_time_per_window)
