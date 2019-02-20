from .graph_controller import GraphAlgorithm
from .graph_model import GraphModel
from .jupyter_view import JupyterView
import time


class Incapy():
    """
    User interface for the Incapy class.

    """

    # Incapy class needs to control all constants, because they are only passed through here
    def __init__(self, filename='../../data/corr_data.h5', model_class=GraphModel,
                 view_class=JupyterView, controller_class=GraphAlgorithm,
                 repulsive_const=1,anim_speed_const=1, update_weight_time=30):
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
        :param repulsive_const: float
            repulsive constant
        :param anima_speed_const: float
            animations speed constant

        """

        self.model = model_class()
        self.view = view_class(self.model, anim_speed_const=anim_speed_const, update_weight_time=update_weight_time)
        self.controller = controller_class(self.model, filename,repulsive_const,anim_speed_const,
                                           update_weight_time)

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

    def update_window(self, value):
        self.controller.update_weights(value)

    def set_repeat(self, value):
        self.controller.set_repeat(value)

    # TODO: Refactor into dictionary
    def notify(self, msg, value=None):
        if msg == 'start':
            self.start()
        elif msg == 'stop':
            self.stop()
        elif msg == 'pause':
            self.pause()
        elif msg == 'play':
            self.play()
        elif msg == 'next_window':
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


    def load_data(self):
        raise NotImplementedError()

