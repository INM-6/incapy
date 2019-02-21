
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

    def __init__(self, model, update_weight_time, anim_speed_const):
        """
        Constructor for the JupyterView class.

        :param model: class
            The model that contains the data to be displayed

        """

        # Initialize the constructor of the abstract base class
        super().__init__(model)

        self.model = model
        self.update_weight_time = update_weight_time
        self.anim_speed_const = anim_speed_const

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
        self.dynamic_map.opts(padding=0.5, tools=['box_select', 'lasso_select', 'tap'], xaxis=None, yaxis=None)\
            .opts(opts.Graph(color_index='index', cmap=['#ff0000', '#00ff00']*50))

        # Register the model
        self._register(model)

        # TODO get min and max from graph controller!! -> will be updated as soon as loader is loaded! default is 30
        self.current_window = widgets.IntSlider(description="Current window", value=1, min=0, max=30,
                                                step=1, orientation='horizontal', disabled=False,
                                                style={'description_width': '8em'})

        self.speed_animation = None
        self.time_to_update_weight = None

        self.out = widgets.Output(layout={'border': '1px solid black'})

    def update_ui(self, msg, value):
        """
        Updates the ui elements of the view.

        :param msg: string
            The message to see what changed.
        :param value:
            The changed value

        :return: None

        """

        if msg == 'window_change':
            # Set the new value of the window_change
            self.current_window.set_trait('value', value=value)

        elif msg == 'window_adjust':
            # Set the new value for the maximum number of windows
            self.current_window.set_trait('max', value=value)

        elif msg == 'speed_constant':
            self.speed_animation.set_trait('value', value=value)

        elif msg == 'weight_time':
            self.time_to_update_weight.set_trait('value', value=value)

    def set_colors(self, colors):
        """
        Sets the colors of the dynamic map

        :param colors: list
            A list of the colors (in hex), where the first element is for the first node, .. etc

        :return: None

        """

        self.dynamic_map.opts(opts.Graph(color_index='index', cmap=colors))

    def show(self):
        """
        Returns the holoviews map in order to display it.

        :return: 'hv.DynamicMap'
            Returns the holoviews map

        """

        from ipywidgets import Layout
        layout = Layout(width='4em')
        slider_style = {'description_width': '8em'}

        play = widgets.Button(description="▶️", layout=layout)
        stop = widgets.Button(description="⏹", layout=layout)
        next = widgets.Button(description="⏭️", layout=layout)

        self.speed_animation = widgets.FloatSlider(description="Animation speed", value=self.anim_speed_const,
                                              min=0.1, max=3.02, step=0.1, orientation='horizontal', style=slider_style)

        self.time_to_update_weight = widgets.IntSlider(description="Time per window", value=self.update_weight_time, min=0,
                                                  max=60, step=1, orientation='horizontal', style=slider_style)

        # Currently not use, but checkbox could also be used instead of toggleButton for repeat
        repeat = widgets.Checkbox(
            value=False,
            description='Repeat',
            disabled=False,
            indent=False
        )

        repeat = widgets.ToggleButton(
            value=False,
            # description='🔁',
            description='⮔',
            layout=layout
        )

        # Horizontal alignment looks nicer than vertical
        # Could also display each button on its own, causing vertical alignment
        animation_controls = widgets.HBox([play, stop, next, repeat])
        box = widgets.VBox([animation_controls, self.current_window, self.time_to_update_weight, self.speed_animation],
                           layout=Layout(justify_content='center'))
        box = widgets.HBox([self.out, box])
        display(box)

        def next_window_action(b):
            self.notify_listeners('next_window')

        next.on_click(next_window_action)

        def reset_action(b):
            self.notify_listeners('reset')
            b.description = '⏹'
            b.on_click(reset_action, remove=True)
            b.on_click(stop_action)
            # XXX
            play.on_click(play_action, remove=True)
            play.on_click(pause_action, remove=True)
            play.on_click(start_action)
            play.description = '▶️'

        def stop_action(b):
            self.notify_listeners('stop')
            b.description = '↻'
            b.on_click(stop_action, remove=True)
            b.on_click(reset_action)

        stop.on_click(stop_action)

        # TODO: These could be refactored into single function
        def play_action(b):
            self.notify_listeners('play')
            b.on_click(play_action, remove=True)
            b.on_click(pause_action)
            b.description = '⏸'

        def pause_action(b):
            self.notify_listeners('pause')
            b.on_click(pause_action, remove=True)
            b.on_click(play_action)
            b.description = '▶️'

        def start_action(b):
            self.notify_listeners('start')
            b.on_click(start_action, remove=True)
            b.on_click(pause_action)
            b.description = '⏸'

        play.on_click(start_action)

        def on_value_change(change):
            self.notify_listeners('speed_change', change['new'])

        self.speed_animation.observe(on_value_change, names='value')

        def time_per_window_change(change):
            self.notify_listeners('update_weight_change', change['new'])

        self.time_to_update_weight.observe(time_per_window_change, names='value')

        def current_window_change(change):
            self.notify_listeners('current_window_change', change['new'])

        self.current_window.observe(current_window_change, names='value')

        def repeat_change(change):
            self.notify_listeners('repeat', change['new'])

        repeat.observe(repeat_change, names='value')
        with self.out:
            display(self.dynamic_map)

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
            edge_source = data[0][0]
            edge_target = data[0][1]
        except IndexError:
            pos_x = []
            pos_y = []
            edge_source = []
            edge_target = []

        vertex_ids = data[1][1]

        new_data = ((edge_source, edge_target), (pos_x, pos_y, vertex_ids))
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
        pass

    def _register(self, model):
        model.add_listener(self)

    def _unregister(self, model):
        model.remove_listener(self)
