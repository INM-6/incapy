
import holoviews as hv
from holoviews import opts
from holoviews.streams import Pipe
from .iview import IView
from IPython.display import display
import ipywidgets as widgets

hv.extension('bokeh')


class JupyterView(IView):
    """
    This class represents the specific view. In that case,
    the view is meant to be displayable for jupyter notebooks.
    Implements the interface IView (extension purposes)

    """

    def __init__(self, model):
        """
        Constructor for the JupyterView class.

        :param model: class
            The model that contains the data to be displayed

        """

        # Initialize the constructor of the abstract base class
        super().__init__(model)

        self.model = model

        # List of all listeners that might need to react to certain input events
        # e.g. button pressed, slider moved
        self.listeners = []
        # TODO: Check using buffer
        # Pipe that gets the updated data that are then sent to the dynamic map
        self.pipe = Pipe(data=[], memoize=True)

        # Holoviews Dynamic map with a stream that gets data from the pipe
        self.dynamic_map = hv.DynamicMap(hv.Graph, streams=[self.pipe])

        # TODO change padding size accordingly
        # Options for the displayed map
        opts.defaults(opts.Graph(width=400, height=400))
        self.dynamic_map.opts(padding=0.5, tools=['box_select', 'lasso_select', 'tap'])\
            .opts(opts.Graph(color_index='index', cmap=['#ff0000', '#00ff00']*50))
        #.options(color='index', cmap='Category10')# xaxis=None, yaxis=None,

        # Register the model
        self._register(model)

        # TODO get min and max from graph controller!!
        self.current_window = widgets.IntSlider(description="Current window", value=1, min=0, max=12,
                                           step=1, orientation='horizontal', disabled=False)

        self.out = widgets.Output(layout={'border': '1px solid black'})

    def update_ui(self, msg, value):
        if msg == 'window_change':
            self.current_window.set_trait('value', value=value)

            pass
            #self.current_window.value = value

    def show(self):
        """
        Returns the holoviews map in order to display it.

        :return: 'hv.DynamicMap'
            Returns the holoviews map

        """

        play = widgets.Button(description="Start")
        stop = widgets.Button(description="Stop")
        skip = widgets.Button(description="Jump to next point in time")

        # Animation speed slider starting at 0.1 because 0 is equivalent to stopping the animation
        # TODO make sure that default value is same as in graph_controller!!
        animation_speed = self.model.get_animation_speed()

        update_weight = self.model.get_time_weight_update()

        speed_animation = widgets.FloatSlider(description="Animation speed", value=animation_speed, min=0.1, max=5,
                                              step=0.1, orientation='horizontal')

        time_to_update_weight = widgets.IntSlider(description="Time to update weight", value=update_weight, min=0,
                                                  max=60, step=1, orientation='horizontal')


        repeat = widgets.Checkbox(
            value=False,
            description='Repeat',
            disabled=False
        )

        # Horizontal alignment looks nicer than vertical
        # Could also display each button on its own, causing vertical alignment
        box = widgets.HBox([play, stop, skip, speed_animation, time_to_update_weight, self.current_window, repeat, self.out])
        display(box)

        def skip_action(b):
            self.notify_listeners('skip')

        skip.on_click(skip_action)

        def reset_action(b):
            self.notify_listeners('reset')
            b.description = 'Stop'
            b.on_click(reset_action, remove=True)
            b.on_click(stop_action)
            # XXX
            play.on_click(play_action, remove=True)
            play.on_click(pause_action, remove=True)
            play.on_click(start_action)
            play.description = 'Start'

        def stop_action(b):
            self.notify_listeners('stop')
            b.description = 'Reset'
            b.on_click(stop_action, remove=True)
            b.on_click(reset_action)

        stop.on_click(stop_action)

        # TODO: These could be refactored into single function
        def play_action(b):
            self.notify_listeners('play')
            b.on_click(play_action, remove=True)
            b.on_click(pause_action)
            b.description = 'Pause'

        def pause_action(b):
            self.notify_listeners('pause')
            b.on_click(pause_action, remove=True)
            b.on_click(play_action)
            b.description = 'Play'

        def start_action(b):
            self.notify_listeners('start')
            b.on_click(start_action, remove=True)
            b.on_click(pause_action)
            b.description = 'Pause'

        play.on_click(start_action)

        def on_value_change(change):
            self.notify_listeners('speed_change', change['new'])

        speed_animation.observe(on_value_change, names='value')

        def time_to_update_weight_change(change):
            self.notify_listeners('update_weight_change', change['new'])

        time_to_update_weight.observe(time_to_update_weight_change, names='value')

        def current_window_change(change):
            self.notify_listeners('current_window_change', change['new'])

        self.current_window.observe(current_window_change, names='value')

        def repeat_change(change):
            self.notify_listeners('repeat', change['new'])

        repeat.observe(repeat_change, names='value')

        return self.dynamic_map


    def update(self, data):
        """
        Gets the x and y positions of the vertices and updates the plot.

        :param data:
            The data containing the new positions of the vertices

        :return: None

        """

        # TODO see if library function in holoviews is available with option to display edges or not
        try:
            pos_x = data[1][0].T[0]
            pos_y = data[1][0].T[1]
        except IndexError:
            pos_x = []
            pos_y = []

        vertex_ids = data[1][1]

        #nodes = hv.Nodes()
        #edges = hv.EdgePaths(([], []))
        new_data = (([], []), (pos_x, pos_y, vertex_ids))
        self.pipe.send(new_data)

    def _register(self, model):
        """
        Adds this class as a listener to the model.

        :param model:
            The model class.
        :return: None

        """

        model.add_listener(self)

    def _unregister(self, model):
        """
        Unregister this class as a listener.

        :param model:
            The model class.
        :return: None

        """

        model.remove_listener(self)

    # XXX
    def add_event_listener(self, listener):
        self.listeners.append(listener)

    # XXX
    def notify_listeners(self, msg, value=None):
        for l in self.listeners:
            l.notify(msg, value)


class NoView(IView):
    """
    For testing purposes only

    """

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
