#from __future__ import print_function
import holoviews as hv
from holoviews.streams import Pipe
from bokeh.io import curdoc, show
from bokeh.layouts import layout
from bokeh.models import Slider, Button
from .iview import IView
from IPython.display import display
import ipywidgets as widgets
from bokeh.resources import INLINE
import bokeh.io
bokeh.io.output_notebook(INLINE)
import time
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
        def modify_doc(doc):
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
            #play = widgets.Button(description="Start")
            stop = widgets.Button(description="Stop")
            # Horizontal alignment looks nicer than vertical
            # Could also display each button on its own, causing vertical alignment
            #box = widgets.HBox([play, stop])
            display(stop)

            play = Button(label='► Play', width=60)
            def stop_action(b):
                self.notify_listeners('stop')
                b.description = 'Stopped'

            stop.on_click(stop_action)

            def play_action():
                self.notify_listeners('play')
                #play.on_click(play_action, remove=True)
                play.on_click(pause_action)
                play.label = 'Pause'

            def pause_action():
                self.notify_listeners('pause')
                #play.on_click(pause_action, remove=True)
                play.on_click(play_action)
                play.label = 'Play'

            def start_action():
                if(play.label == '► Play'):
                    self.notify_listeners('start')
                    play.label = 'Pause'
                elif play.label == 'Pause':
                    self.notify_listeners('pause')
                    play.label = 'Play'
                elif play.label == 'Play':
                    self.notify_listeners('play')
                    play.label = 'Pause'
                #play.on_click(start_action, remove=True)
                #play.on_click(pause_action)
                #play.label = 'Pause'

            play.on_click(start_action)

            renderer = hv.renderer('bokeh')
            plot = renderer.get_plot(self.dynamic_map)

            mylayout = layout([
                [plot.state],
                [play],
            ], sizing_mode='fixed')

            doc.add_root(mylayout)

            #show(mylayout)

            # For layouting
            #out = widgets.Output()

            # show(play)
            #with out:
            #display(self.dynamic_map)

            #display(mylayout)

        show(modify_doc, notebook_url="http://localhost:8888")
        return #play

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
    def notify_listeners(self, msg):
        print("Hallo!!")
        for l in self.listeners:
            l.notify(msg)


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
