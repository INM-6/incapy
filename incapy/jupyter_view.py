import holoviews as hv
from holoviews.streams import Pipe
from .iview import IView
import numpy as np
hv.extension('bokeh')


class JupyterView(IView):

    def __init__(self, model):
        super().__init__(model)

        self.model = model
        slide_range_update = np.arange(0, 61, 1)
        slide_range_animation = np.arange(0, 1.1, 0.1)
        sliders = [hv.Dimension(('time_to_update_weights', ' '), default=self.model.time_to_update_weights, values=slide_range_update),
                   hv.Dimension(('animation_speed', ' '), default=self.model.animation_speed, values=slide_range_animation)]
        # TODO: Check using buffer
        self.pipe = Pipe(data=[], memoize=True)
        self.dynamic_map = hv.DynamicMap(self.update_plot, streams=[self.pipe], kdims=sliders)
        # self.dynamic_map = self.dynamic_map.redim.values(time_to_update_weights=slide_range_update, animation_speed=slide_range_animation)

        # TODO change padding size accordingly
        self.dynamic_map.opts(padding=0.5)# xaxis=None, yaxis=None,
        self._register(self.model)

    def update_plot(self, data, time_to_update_weights, animation_speed):
        print("in update plot!!!")
        # Change values in model
        self.model.set_time_weight_update(time_to_update_weights)
        self.model.set_animation_speed(animation_speed)

        return hv.Graph(data)

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
