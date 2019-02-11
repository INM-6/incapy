from .graph_controller import GraphAlgorithm
from .graph_model import GraphModel
from .jupyter_view import JupyterView


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

    def show(self):
        """
        Show the map.

        :return: The view.

        """
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
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def load_data(self):
        raise NotImplementedError()

