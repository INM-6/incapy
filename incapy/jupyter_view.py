import holoviews as hv
from holoviews.streams import Pipe
from .iview import IView
hv.extension('bokeh')


class JupyterView(IView):

    def __init__(self, model):
        super().__init__(model)
        # TODO: Check using buffer
        self.pipe = Pipe(data=[], memoize=True)
        self.dynamic_map = hv.DynamicMap(hv.Graph, streams=[self.pipe])
        # TODO change padding size accordingly
        self.dynamic_map.opts(padding=0.1)# xaxis=None, yaxis=None,
        self._register(model)

    def show(self):
        return self.dynamic_map

    def update(self, data):
        # TODO see if library function in holoviews is available with option to display edges or not
        try:
            pos_x = (data[1][0].T)[0]
            pos_y = (data[1][0].T)[1]
        except IndexError:
            pos_x = []
            pos_y = []

        new_data = (([], []), (pos_x,pos_y,data[1][1]))
        self.pipe.send(new_data)
        # print(self.dynamic_map.streams)

    def _register(self, model):
        model.add_listener(self)

    def _unregister(self, model):
        model.remove_listener(self)


class NoView(IView):

    def __init__(self, model):
        super().__init__(model)
        self._register(model)

    def show(self):
        pass

    def update(self, data):
        print(id(data[0][0]))
        pass

    def _register(self, model):
        model.add_listener(self)

    def _unregister(self, model):
        model.remove_listener(self)
