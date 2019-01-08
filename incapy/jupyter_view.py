import holoviews as hv
from holoviews.streams import Pipe
from incapy.iview import IView
hv.extension('bokeh')


class JupyterView(IView):

    def __init__(self, model):
        super().__init__(model)
        self.pipe = Pipe(data=[])
        self.dynamic_map = hv.DynamicMap(hv.Graph, streams=[self.pipe])
        # TODO change padding size accordingly
        self.padding = dict(x=(-0.2, 1.2), y=(-0.2, 1.2))
        self.dynamic_map.redim.range(**self.padding)
        self._register(model)

    def show(self):
        return self.dynamic_map

    def update(self, data):
        self.pipe.send(data)
        print(self.dynamic_map.streams)

    def _register(self, model):
        model.add_listener(self)

    def _unregister(self, model):
        model.remove_listener(self)



