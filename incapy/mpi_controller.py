from .graph_controller import GraphAlgorithm

import threading
import os
import numpy as np
import time
from mpi4py import MPI

class MPI_Controller(GraphAlgorithm):

    def __init__(self, model, filename, dataloader, repulsive_const, anim_speed_const, update_weight_time):
        """
        Constructor for the GraphAlgorithm class. Initializes all attributes.

        :param model:
            The model class
        :param filename: string
            The filename to the data to be loaded
        :param repulsive_const: float
            repusive constant
        :param anim_speed_const: float
            animation speed constant
        :param dataloader: class
            The dataloader class

        """

        # Needed for threading
        self.wait_event = threading.Event()
        self.mutex = threading.Lock()
        self.run_thread = None

        # Flag that is set to stop or pause execution
        self.stop = False

        self.model = model

        # Load the data
        # TODO should not be needed any more later
        self.loader = dataloader()
        self.loader.positions = np.array(np.meshgrid(np.arange(10), np.arange(10)))
        arr = np.ndarray((100, 3))
        arr[:, 1] = np.hstack(self.loader.positions[0])
        arr[:, 2] = np.hstack(self.loader.positions[1])
        self.loader.positions = arr
        self.loader.vertex_ids = np.arange(100)
        self.loader.number_windows = 1
        self.loader.edge_ids = np.empty((5050, 2), dtype=np.int32)
        # count = 0
        import itertools as it
        self.loader.edge_ids = np.array(list(it.combinations(self.loader.vertex_ids, 2)))
        # for i in range(100):
        #     for j in range(i, 100):
        #         self.loader.edge_ids[count][0] = i
        #         self.loader.edge_ids[count][1] = j
        #         count += 1
        #with open("test", mode='w+') as f:
        # print("{}".format(count))
        # self.loader.load_data(filename)

        # Populate the model with the data
        self.populate_model()

        # NOTE: edge_threshold needs to be set before calling update weights
        # TODO should not be needed any more later
        self.current_window = -1

        # Default value for threshold that determines which edges should be shown
        self.edge_threshold = 0.6

        self.raw_corr = np.zeros((len(self.model.vertex_ids), len(self.model.vertex_ids)), dtype=np.float64)
        #
        # self.set_edge_threshold(self.edge_threshold)

        # Constants needed for the force-directed layout algorithm
        self.natural_spring_length = None
        # TODO: Calculate center
        self.graph_center = None
        # TODO: Should be changeable by user (interactively?)
        self.repulsive_const = repulsive_const  # Daniel: 1
        self.anim_speed_const = anim_speed_const
        # 1/20 is replacement for time since last frame (i.e. frame rate would be 20Hz)
        self.max_step_size = self.anim_speed_const/20   # Daniel: 0.9, is however changed every step
        # Get default from file or incapy constructor

        # The color attributes for the nodes
        self.hex_colors = None
        self.get_color_attributes()

        # Repeat is by default false, meaning that after the last window, no more windows will be loaded
        self.repeat = False

        # The time (in seconds) when to load the new window
        self.update_weight_time = update_weight_time

        # # FOR MPI
        self.model.set_weights(np.zeros((len(self.model.vertex_ids), len(self.model.vertex_ids)), dtype=np.float64), 0)
        self.data_received_event = threading.Event()
        self.data_received_event.clear()

        self.init_algorithm()

        # # self.raw_corr = None
        #
        # self.comm = MPI.COMM_WORLD
        # rank = self.comm.Get_rank()
        # self.start_mpi_thread()

    def start_mpi_thread(self):

        # Init connection
        # fport_path = "visport_in.txt"
        # print("Waiting for file")
        # while not os.path.exists(fport_path):
        #     print("Still waiting")
        #     pass
        # fport = open(fport_path, "r")
        # port = fport.read()
        # fport.close()
        #
        # self.sim_comm = self.comm.Connect(port, MPI.INFO_NULL, root=0)
        #
        # rank_sim = self.sim_comm.Get_rank()

        mpi_thread = threading.Thread(target=self.thread_runnable)
        mpi_thread.start()

    def thread_runnable(self):

        data = np.empty((len(self.model.vertex_ids), len(self.model.vertex_ids)))

        while True:
            # status = None
            # print("Waiting for actual data")
            # self.sim_comm.Recv([data, MPI.FLOAT], source=0, tag=MPI.ANY_TAG, status=status)
            # print("Received data")
            time.sleep(0.01)
            data = np.random.rand(*data.shape)
            self.set_matrix_from_mpi(data)#
        #fport_path = "visport_in.txt"
        # print("Waiting for file")
        # while not os.path.exists(fport_path):
        #     print("Still waiting")
        #     pass
        # fport = open(fport_path, "r")
        # port = fport.read()
        # fport.close()
            self.data_received_event.set()

    def set_edge_threshold(self, threshold=None):
        """
         Sets the edge threshold (all edges greater than the threshold are displayed)

         :param threshold: float
             The edge threshold

         :return: None

         """

        # If threshold has been provided,
        if threshold is not None:
            # Use that threshold
            self.edge_threshold = threshold
        # Check directly from given values, without any transformation
        # Can be changed to use transformed weights instead, if it becomes necessary
        # to remove x_corr from memory
        mask = self.raw_corr[np.triu_indices(len(self.model.vertex_ids))] > self.edge_threshold
        self.model.set_edge_threshold_mask(mask)

    def set_matrix_from_mpi(self, data):
        # TODO: Get from MPI
        # self.raw_corr = self.loader.weights[1]*(-1)+1
        self.raw_corr = data
        # TODO: Modularize
        with self.mutex:
            self.model.set_weights(self.weights_from_corr_linear(self.raw_corr), 0)
            self.set_edge_threshold()

    def next_window(self, value=None):
        pass

    def run_iteration(self):
        """
        Orchestrating function for running the animation.

        :return: None

        """

        self.start_mpi_thread()

        # TODO make skip weights based on number of iterations (reproducability)
        self.data_received_event.wait()

        with open("test", mode='w+') as f:
            f.write("Hilfe")

        # Time is needed for updating weights after certain time (update_weight_time)
        last_time = time.time()
        self.current_window_time = last_time

        # TODO needs to be changed
        # self.next_window(0)
        self.init_algorithm()

        # TODO: Maybe catch Keyboard interrupt to output position

        while True:
            # Wait for other events
            self.wait_event.wait()
            # If stop is requested,
            if self.stop:
                # stop the run_iteration
                break

            # This makes the speed of the animation constant
            # Even if the framerate drops, vertices will move at about the same speed
            curr_time = time.time()
            dt = curr_time - last_time
            last_time = curr_time

            # dt must be bounded, in case of string lag positions should not jump too far
            dt = min(dt, 0.1)
            self.max_step_size = self.anim_speed_const * dt

            # # Load the new window, if the update_weight_time is reached
            # if curr_time - self.current_window_time > self.update_weight_time:
            #     if self.update_weight_time != 0:
            #         self.next_window()
            #     # Note: Needs to be set so if slider that specifies time per window is moved away from 0,
            #     # the window will not be switched immediately!!! So time needs to be around 0 at any moment
            #     # when self.update_weight_time is 0
            #     self.current_window_time = curr_time

            # Is not reached
            with open("test", mode='w+') as f:
                f.write("almost{}".format(time.time()))
            with self.mutex:
                # The function to calculate the new positions
                self.do_step()
