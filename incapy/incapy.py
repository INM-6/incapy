from .graph_controller import GraphAlgorithm
from .graph_model import GraphModel
from .jupyter_view import JupyterView


class Incapy():

    def __init__(self, filename='../../data/corr_data.h5', model_class=GraphModel, view_class=JupyterView, controller_class=GraphAlgorithm):
        self.model = model_class()
        self.view = view_class(self.model)
        self.controller = controller_class(self.model, filename)

    def show(self):
        # XXX
        self.view.add_event_listener(self)
        return self.view.show()

    def add_view(self, view):
        raise NotImplementedError()

    def start(self):
        self.controller.start_iteration()

    def stop(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def load_data(self):
        raise NotImplementedError()

