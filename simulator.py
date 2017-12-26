# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""
import time
import sim_time
from deferred_update import UpdateType, DeferredUpdate
import numpy as np


class Simulator(object):
    """
    Main simulation controller
    Singleton Pattern
    A note on patterns: http://stackoverflow.com/questions/1318406/why-is-the-borg-pattern-better-than-the-singleton-pattern-in-python
    """
    # reference to single instance
    __single = None
    # simulation time object
    __time = None
    # GUI object
    __gui = None
    # list of objects processed when running
    __object_list = None
    # objects that require updating at end of a time step
    __update_list = None
    # class control that can be used to determine what can only be done before/during or after a run.
    run_done = None

    def __init__(self, _gui=True):
        """
            Internal method, but allows explicit instantiation (or not) of a GUI at initial setup of the Simulator
            instance. Should only be called if it can be guaranteed Simulator instance is new.
            Should use get_instance() instead to get existing instance, or create a new one if it does not exist.

            :raises RuntimeError if called when there is an existing Simulator object
        """
        if not Simulator.__single:
            Simulator.__time = sim_time.Time()
            Simulator.__object_list = []
            Simulator.__update_list = []
            if _gui:
                import gui
                Simulator.__gui = gui.GUI.init(Simulator.__time)
            Simulator.__single = self
        else:
            raise RuntimeError('A Simulator already exists')

    @classmethod
    def get_instance(cls):
        """
        Get existing Simulator instance, or create a new one and return it.

        :return: Simulator instance

        Usage:
            sim = Simulator.get_instance()
        """
        if not cls.__single:
            cls.__single = Simulator()
        return cls.__single

    @classmethod
    def run(cls, continuefor: np.float64 = None, stop: np.float64 = None, dt: np.float64 = None, plot_update_interval: float = 100,
            data_collect_interval: np.float64 = None, block_after=False, print_time=True):
        """
        Run a time-based simulation.
        Each time-registered object is moved forward by dt

        :param continuefor: how long simulation should continue for
        :param stop: time to stop simulation
        :param dt: time step to use for simulation run
        :param plot_update_interval: frequency to update graphs (in s)
        :param data_collect_interval: frequency to collect data for plotting (in s)
        :param block_after: does gui cause a pause/block after run is finished. If True, graphs close immediately upon
        completion (default: False)
        :param print_time: whether to log to the console the simulation time moved forward and length of time taken
        """
        # assign default values if not specified
        if stop is None:
            stop = cls.__time.stop
        if continuefor is not None:
            stop = cls.__time.time + np.float64(continuefor)
        if dt is None:
            dt = cls.__time.dt
        if data_collect_interval is None:
            data_collect_interval = dt
        if plot_update_interval < data_collect_interval:
            data_collect_interval = plot_update_interval
        # create variables for faster processing during loop
        data_collect_interval_dt = (data_collect_interval / dt)
        plot_update_interval_dt = (plot_update_interval / dt)
        if print_time:
            print("running from {0:f} s until {1:f} s with time step of {2} seconds ".format(cls.__time.time, stop, dt))        # get state ready for run
        cls.run_done = False
        if continuefor is None:
            cls.__time.reset()
            cls.clear_graphs()
        time.clock()
        # set timestep value
        cls.__time.stepsize(dt)
        # go through a simulation
        t_start = int(round(cls.__time.time / dt))
        t_stop = int(round(stop / dt))
        for t in range(t_start, t_stop):
            if t % data_collect_interval_dt == 0:
                cls.update_graphs()
            if t % plot_update_interval_dt == 0:
                cls.plot_graphs()
            # go through each object and process it's step
            for compartment in cls.__object_list:
                compartment.step(cls.__time)
            for colormap in cls.__object_list:
                colormap.step(cls.__time)
            # move global time step forward
            cls.__time.step()
            # apply updates to objects that required deferred updating of their variables
            cls.__apply_updates()
        cls.run_done = True
        # allows for delayed display
        if continuefor is not None and (continuefor - plot_update_interval) >= 0:
            cls.update_graphs()
            cls.plot_graphs()
        if print_time:
            print("time taken: {}".format(time.clock()))
        if block_after and cls.__gui is not None:
            cls.plot_graphs()
            cls.__gui.block()

    @classmethod
    def register_compartment(cls, compartment):
        """
        Add compartment to list of compartments to be updated at each time step

        :param compartment:
        :return:
        :raise TypeError if compartment not an instance of Compartment

        Usage:
        Within a class:
            Simulator.get_instance().register_compartment(self)
        """
        if isinstance(compartment, sim_time.TimeMixin):
            cls.__object_list.append(compartment)
        else:
            raise TypeError("Compartment instance expected {0} given".format(type(compartment)))

    @classmethod
    def register_colormap(cls, colormap):
        """
        As above but for colormap object (compartment heights)
        :param colormap:
        :return:
        """
        if isinstance(colormap, sim_time.TimeMixin):
            cls.__object_list.append(colormap)
        else:
            raise TypeError("Compartment instance expected {0} given".format(type(colormap)))

    @classmethod
    def to_update(cls, obj: object, var: str, value: any, update_type: UpdateType):
        """
        Stores the value change for a var to be applied at the end of the time step.

        :param obj: object that the variable is a member of
        :param var: variable of the object to be updated
        :param value: the value to be updated at the end of the time step
        :param update_type: the type of update to apply to the variable
        """
        cls.__update_list.append(DeferredUpdate(obj, var, value, update_type))

    @classmethod
    def to_update_multi(cls, obj: object, d: dict):
        """
        Allow multiple deferred updates to be referenced through a dictionary.

        :param obj: object that the variable is a member of
        :param d: dictionary of variables as keys and values as dictionaries with keys 'value' and 'type'

         Usage:
        Within a class:
            Simulator.get_instance().to_update_multi(self, {
                'nai': {
                    "value": dnai,
                    "type": UpdateType.CHANGE
                }, 'ki': {
                    "value": dki,
                    "type": UpdateType.CHANGE
                }, 'cli': {
                    "value": dcli,
                    "type": UpdateType.CHANGE
                }
            })

        """
        for var, sub_dict in d.items():
            cls.to_update(obj, var, sub_dict["value"], sub_dict["type"])

    @classmethod
    def to_update_change(cls, obj, var, delta_value):
        """
        Stores the value change for a var to be applied at the end of the time step.
        Convenient method so UpdateType does not need to specified as CHANGE

        :param obj: object that the variable is a member of
        :param var: variable of the object to be updated
        :param delta_value: the change in value to be updated at the end of the time step

        Usage:
        Within a class
            Simulator.get_instance().to_update(self, self.name_of_variable, self.update_value)
        """
        cls.__update_list.append(DeferredUpdate(obj, var, delta_value, UpdateType.CHANGE))

    @classmethod
    def to_update_set(cls, obj, var, value):
        """
        Stores the value for a var to be set to at the end of the time step.

        :param obj: object that the variable is a member of
        :param var: variable of the object to be set
        :param value: the value to be set to at the end of the time step

        Usage:
        Within a class
            Simulator.get_instance().to_update(self, self.name_of_variable, self.set_value)
        """
        cls.__update_list.append(DeferredUpdate(obj, var, value, UpdateType.SET))

    @classmethod
    def __clear_updates(cls):
        """
        Empty deferred update list (set to []).
        """
        cls.__update_list = []

    @classmethod
    def __apply_updates(cls):
        """
        Apply all deferred updates and then clear the list.
        """
        for deferred_update in cls.__update_list:
            deferred_update.apply_update()
        cls.__clear_updates()

    @classmethod
    def clear_graphs(cls):
        """
        Call all GUI's graphs to clear their contents
        """
        if cls.__gui is not None:
            cls.__gui.clear_graphs()

    @classmethod
    def update_graphs(cls):
        """
        Call all GUI's graphs to update their values (does not mean plot)
        """
        if cls.run_done is False:
            if cls.__gui is not None:
                cls.__gui.update_graphs()

    @classmethod
    def plot_graphs(cls):
        """
        Call all GUI's graphs to plot their contents
        """
        if cls.__gui is not None:
            cls.__gui.plot_graphs()

    @classmethod
    def time(cls):
        """
        Get Time control
        Warning: time is a python library and so assigned variable should not be named such.

        :return: Time object

        Usage:
            sim_time = Simulator.get_instance().time()
        """
        return cls.__time

    @classmethod
    def gui(cls):
        """
        Get GUI.
        Creates GUI if called and GUI does not exist.

        :return: GUI object reference

        Usage:
            sim_time = Simulator.get_instance().gui()
        """
        if cls.__gui is None:
            import gui
            Simulator.__gui = gui.GUI.init(Simulator.__time)
        return cls.__gui

    @classmethod
    def object_list(cls, add=None):
        """
        Retrieve and optionally add to object list.
        Used for testing. Should use register_compartment instead.

        :param add: Object to be added
        :return: object list
        """
        if add is not None:
            cls.__object_list.append(add)
        return cls.__object_list

    @classmethod
    def dispose(cls):
        """
        Cleaning of class.
         Note: objects are not garbage collected explicitly, i.e. they still exist in memory.
        """
        cls.__single = None
        cls.__time = None
        cls.__gui = None
        cls.__object_list = None
        cls.__update_list = None
