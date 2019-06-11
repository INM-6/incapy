from incapy.fd_layout import FDLayout
from .file_controller import FileController
from .graph_model import GraphModel
from .jupyter_view import JupyterView
from .load_data import DataLoader
from .mpi_controller import MPIController


class Incapy():
    """
    User interface for the Incapy class.

    """
    # Incapy class needs to control all constants, because they are only passed through here
    def __init__(self, repulsive_const=1, anim_speed_const=1, time_per_window=30,
                 model_class=GraphModel, view_class=JupyterView, controller_class=FileController,
                 **kwargs):
        """
        Constructor for the Incapy class.

        :param filename: string
            The filename for the data to be loaded
        :param model_class: class
            The model class
        :param view_class: class
            The view class
        :param controller_class: class
            The controller class
        :param data_loader_class: class
            The data loader class
        :param repulsive_const: float
            repulsive constant
        :param anim_speed_const: float
            animation speed constant
        :param edge_threshold: float
            display all edges greater than the threshold

        """

        # Instantiate the classes, NOTE: do not change order
        self.model = model_class()
        self.anim_speed_const = anim_speed_const
        self.repulsive_const = repulsive_const
        self.time_per_window = time_per_window
        self.view =view_class(self.model, anim_speed_const=anim_speed_const, time_per_window=time_per_window, **kwargs)
        self.controller = controller_class(self.model, repulsive_const=repulsive_const, anim_speed_const=anim_speed_const,
                                           time_per_window=time_per_window, **kwargs)

    # TODO: Encapsulate algorithm and pass it alone, separate from controller
    # TODO: Generic view for all vs. MPIView specific for MPI; maybe split into wrapper for use case and central display
    # TODO: Do not use JupyterView
    def init_mpi(self, view_class=JupyterView, algorithm=FDLayout, **mpiargs):
        self.view = view_class(self.model, anim_speed_const=self.anim_speed_const, time_per_window=self.time_per_window)
        self.controller = MPIController(self.model, repulsive_const=self.repulsive_const, anim_speed_const=self.anim_speed_const,
                                        time_per_window=self.time_per_window, algorithm=algorithm)

    def init_file(self, filename, view_class=JupyterView, algorithm=FDLayout, data_loader=DataLoader, **fileargs):
        self.view = view_class(self.model, anim_speed_const=self.anim_speed_const, time_per_window=self.time_per_window)
        self.controller = FileController(self.model, repulsive_const=self.repulsive_const, anim_speed_const=self.anim_speed_const,
                                         time_per_window=self.time_per_window, filename=filename, data_loader=data_loader, algorithm=algorithm)

    def init_elephant(self, ccm, view_class=JupyterView, algorithm=FDLayout, **elephargs):
        self.view = view_class(self.model, anim_speed_const=self.anim_speed_const, time_per_window=self.time_per_window)
        self.controller = EleController(self.model, repulsive_const=self.repulsive_const, anim_speed_const=self.anim_speed_const,
                                           time_per_window=self.time_per_window, ccm=ccm, algorithm=algorithm)

    def show(self, edge_threshold=0.4):
        """
        Shows the view and registers for events happening in the view.

        :return: The view to be displayed.

        """
        # Register for events happening in View
        self.view.add_event_listener(self)

        return self.view.show()

    def add_view(self, view):
        """
        Adds another view to the listeners.

        :param view:
            The view to be added
        :return: None

        """

        self.model.add_listener(view)

    def start(self):
        """
        Starts the animation.

        :return: None
        
        """

        self.controller.start_iteration()

    def stop(self):
        """
        Stops the animation.

        :return: None

        """

        self.controller.stop_iteration()

    def pause(self):
        """
        Pauses the animation.

        :return: None

        """

        self.controller.pause_iteration()

    def play(self):
        """
        Continues/Starts the animation.

        :return: None

        """

        self.controller.continue_iteration()

    def next_window(self):
        """
        Skips the current window and moves on to the next window.

        :return: None

        """
        with open("test2", mode="w+") as f:
            print(self.controller.next_window, file=f)
        self.controller.next_window()

    def reset(self):
        """
        Resets the animation to the starting position.

        :return: None

        """

        self.controller.reset()

    def change_speed(self, value):
        """
        Changes the animation speed to 'value'.

        :param value: float
            The animation speed

        :return: None

        """

        self.controller.set_anim_speed_const(value)

    def time_per_window_change(self, value):
        """
        Sets the time to load the next window to 'value'.

        :param value: int
            The time (in seconds) to load the next window

        :return: None

        """

        self.controller.set_time_per_window(value)

    def update_window(self, value):
        """
        Sets the current window to 'value'.

        :param value: int
            The window to be loaded from the data

        :return: None

        """

        self.controller.next_window(value)

    def set_repeat(self, value):
        """
        Sets repeat to 'value', meaning that when at the last window, iteration at the first
        window will start again.

        :param value: boolean
            True, if repeat is requested, else False

        :return: None

        """

        self.controller.set_repeat(value)

    # TODO: Refactor into dictionary
    def notify(self, msg, value=None):
        """

        :param msg: string
            The message that is sent from the view.

        :param value:
            The value that changed in the view.

        :return: None

        """

        if msg == 'start':
            self.start()
        elif msg == 'stop':
            self.stop()
        elif msg == 'pause':
            self.pause()
        elif msg == 'play':
            self.play()
        elif msg == 'next_window':
            self.next_window()
        elif msg == 'reset':
            self.reset()
        elif msg == 'speed_change':
            self.change_speed(value)
        elif msg == 'update_weight_change':
            self.time_per_window_change(value)
        elif msg == 'current_window_change':
            self.update_window(value)
        elif msg == 'repeat':
            self.set_repeat(value)
