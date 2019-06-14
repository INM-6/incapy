from .controller import Controller
import time


class FileController(Controller):
    """

    The concrete controller. All the calculations are handled here.
    Controls all the transactions and interactions.

    """

    changeable_values = ("repeat", "time_per_window", "current_window")

    def __init__(self, model, view, filename, data_loader, repulsive_const, anim_speed_const, time_per_window, **kwargs):
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
        :param data_loader: class
            The dataloader class

        """

        # Load the data
        self.loader = data_loader()
        self.filename = filename

        super().__init__(model, view, repulsive_const=repulsive_const, anim_speed_const=anim_speed_const)

        # NOTE: edge_threshold needs to be set before calling update weights
        self.current_window = -1

        # Repeat is by default false, meaning that after the last window, no more windows will be loaded
        self.repeat = False

        # The time (in seconds) when to load the new window
        self.time_per_window = time_per_window

    def get_metadata(self):
        return self.loader.load_data(filename=self.filename)

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
            self.raw_corr = self.loader.raw_corr[curr_window]
            with self.mutex:
                self.model.set_weights(self.algorithm.weights_from_corr_linear(self.raw_corr), curr_window)
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

    def set_repeat(self, value):
        """
        Sets the repeat value.

        :param value: bool
            'True' when repeat is requested, else 'False'

        :return: None

        """

        self.repeat = value

    # Correctly set window if changed
    current_window = property(lambda self: self.current_window, next_window)
