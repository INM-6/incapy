
from .graph_controller import GraphAlgorithm
from .graph_model import GraphModel
from .jupyter_view import JupyterView
from .load_data import DataLoader


class Incapy():
    """
    User interface for the Incapy class.

    """

    def __init__(self, filename='../../data/corr_data.h5', model_class=GraphModel, view_class=JupyterView,
                 controller_class=GraphAlgorithm, data_loader_class = DataLoader, repulsive_const=1, anim_speed_const=1, update_weight_time=30,
                 edge_threshold=0.6):
        """
        Constructor for the Incapy class.

        :param filename: string
            The filename for the data to be loaded
        :param model_class: class
            The model class
        :param view_class: class
            The view class
        :param controller_class: class
            The controller class
        :param data_loader_class: class
            The data loader class
        :param repulsive_const: float
            repulsive constant
        :param anim_speed_const: float
            animation speed constant
        :param edge_threshold: float
            display all edges greater than the threshold

        """

        # Instantiate the classes
        self.model = model_class()
        self.view = view_class(self.model)
        self.controller = controller_class(self.model, filename, data_loader_class, repulsive_const, anim_speed_const,
                                           update_weight_time, edge_threshold)

    def show(self):
        """
        Shows the view and registers for events happening in the view.

        :return: The view to be displayed.

        """

        # Register for events happening in View
        self.view.add_event_listener(self)

        return self.view.show()

    def add_view(self, view):
        """
        Adds another view to the listeners.

        :param view:
            The view to be added
        :return: None

        """

        self.model.add_listener(view)

    def start(self):
        """
        Starts the animation.

        :return: None
        
        """

        self.controller.start_iteration()

    def stop(self):
        """
        Stops the animation.

        :return: None

        """

        self.controller.stop_iteration()

    def pause(self):
        """
        Pauses the animation.

        :return: None

        """

        self.controller.pause_iteration()

    def play(self):
        """
        Continues/Starts the animation.

        :return: None

        """

        self.controller.continue_iteration()

    def skip(self):
        """
        Skips the current window and moves on to the next window.

        :return: None

        """

        self.controller.update_weights()

    def reset(self):
        """
        Resets the animation to the starting position.

        :return: None

        """

        self.controller.reset()

    def change_speed(self, value):
        """
        Changes the animation speed to 'value'.

        :param value: float
            The animation speed

        :return: None

        """

        self.controller.set_anim_speed_const(value)

    def update_weight_change(self, value):
        """
        Sets the time to load the next window to 'value'.

        :param value: int
            The time (in seconds) to load the next window

        :return: None

        """

        self.controller.set_update_weight_time(value)

    def update_window(self, value):
        """
        Sets the current window to 'value'.

        :param value: int
            The window to be loaded from the data

        :return: None

        """

        self.controller.update_weights(value)

    def set_repeat(self, value):
        """
        Sets repeat to 'value', meaning that when at the last window, iteration at the first
        window will start again.

        :param value: boolean
            True, if repeat is requested, else False

        :return: None

        """

        self.controller.set_repeat(value)

    # TODO: Refactor into dictionary
    def notify(self, msg, value=None):
        """

        :param msg: string
            The message that is sent from the view.

        :param value:
            The value that changed in the view.

        :return: None

        """

        if msg == 'start':
            self.start()
        elif msg == 'stop':
            self.stop()
        elif msg == 'pause':
            self.pause()
        elif msg == 'play':
            self.play()
        elif msg == 'skip':
            self.skip()
        elif msg == 'reset':
            self.reset()
        elif msg == 'speed_change':
            self.change_speed(value)
        elif msg == 'update_weight_change':
            self.update_weight_change(value)
        elif msg == 'current_window_change':
            self.update_window(value)
        elif msg == 'repeat':
            self.set_repeat(value)
