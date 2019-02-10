#from __future__ import print_function
import holoviews as hv
from holoviews.streams import Pipe
from bokeh.io import curdoc, show
from bokeh.layouts import layout
from bokeh.models import Slider, Button
from .iview import IView
from IPython.display import display
import ipywidgets as widgets
hv.extension('bokeh')


class JupyterView(IView):

    def __init__(self, model):
        super().__init__(model)
        # List of all listeners that might need to react to certain input events
        # e.g. button pressed, slider moved
        self.listeners = []
        # TODO: Check using buffer
        self.pipe = Pipe(data=[], memoize=True)
        self.dynamic_map = hv.DynamicMap(hv.Graph, streams=[self.pipe])
        # TODO change padding size accordingly
        self.dynamic_map.opts(padding=0.5)# xaxis=None, yaxis=None,
        self._register(model)


    def show(self):
        # renderer = hv.renderer('bokeh').instance(mode='server')
        # # renderer.app(self.dynamic_map, show=True, websocket_origin='localhost:8888')
        # plot = renderer.get_plot(self.dynamic_map, curdoc())
        # button = Button(label='► Play', width=60)
        # button.on_click(self.notify_listeners)
        # self.layout = layout([
        #     [plot.state],
        #     [button],
        # ], sizing_mode='fixed')
        # curdoc().add_root(self.layout)
        # show(self.layout, notebook_url='localhost:8888')
        button = widgets.Button(description="Click Me!")
        display(button)

        def onClick(b):
            b.description = 'Clicked'
            self.notify_listeners()
        button.on_click(onClick)
        #self.notify_listeners()
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

    # XXX
    def add_event_listener(self, listener):
        self.listeners.append(listener)

    # XXX
    def notify_listeners(self):
        print("Hallo!!")
        for l in self.listeners:
            l.start()


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
