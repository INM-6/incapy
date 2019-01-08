from incapy.graph_controller import GraphAlgorithm
from incapy.graph_model import GraphModel
from incapy.jupyter_view import JupyterView


class Incapy():

    def __init__(self, model_class=GraphModel, view_class=JupyterView, controller_class=GraphAlgorithm):
        raise NotImplementedError()

    def add_view(self, view):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def load_data(self):
        raise NotImplementedError()


