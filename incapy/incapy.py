from .graph_controller import GraphAlgorithm
from .graph_model import GraphModel
from .jupyter_view import JupyterView
import time


class Incapy():
    """
    User interface for the Incapy class.

    """

    def __init__(self, filename='../../data/corr_data.h5', model_class=GraphModel, view_class=JupyterView, controller_class=GraphAlgorithm):
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

        """

        self.model = model_class()
        self.view = view_class(self.model)
        self.controller = controller_class(self.model, filename)

    def show(self, edge_threshold=0.6):
        """
        Show the map.

        :return: The view.

        """
        # Define all parameters required for display
        self.controller.set_edge_threshold(edge_threshold)
        # Register for events happening in View
        self.view.add_event_listener(self)
        return self.view.show()

    def add_view(self, view):
        raise NotImplementedError()

    def start(self):
        """
        Start the animation.

        :return: None
        
        """
        self.controller.start_iteration()

    def stop(self):
        self.controller.stop_iteration()

    def pause(self):
        self.controller.pause_iteration()

    def play(self):
        self.controller.continue_iteration()

    def skip(self):
        self.controller.update_weights()

    def reset(self):
        self.controller.reset()

    def change_speed(self, value):
        self.controller.set_anim_speed_const(value)

    def update_weight_change(self, value):
        self.controller.set_update_weight_time(value)

    # TODO: Refactor into dictionary
    def notify(self, msg):
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

    def notify_sliders(self, msg, value):
        if msg == 'speed_change':
            self.change_speed(value)
        elif msg == 'update_weight_change':
            self.update_weight_change(value)



    def load_data(self):
        raise NotImplementedError()

