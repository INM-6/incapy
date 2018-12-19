

class Incapy():

    def __init__(self, model_class, view_class, controller_class):
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


