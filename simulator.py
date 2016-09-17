# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
from enum import Enum
from collections import OrderedDict
import sim_time
from compartment import Compartment
import time
from threading import Timer


class UpdateType(Enum):
    CHANGE = 1
    SET = 2
    FUNCTION = 3
    FUNCTION_RETURN = 4
    EVAL = 5
    EVAL_RETURN = 6


class DeferredUpdate:
    def __init__(self, obj, var, value, update_type: UpdateType):
        self.obj = obj
        self.var = var
        self.value = value
        self.update_type = update_type

    def apply_update(self):
        if self.update_type == UpdateType.CHANGE:
            self.obj[self.var] += self.value
        elif self.update_type == UpdateType.SET:
            self.obj[self.var] = self.value
        elif self.update_type == UpdateType.FUNCTION:
            self.value()
        elif self.update_type == UpdateType.FUNCTION_RETURN:
            self.obj.var = self.value()
        elif self.update_type == UpdateType.EVAL:
            eval(self.value)
        elif self.update_type == UpdateType.EVAL:
            self.obj.var = eval(self.value)


class Simulator:
    """
    Main simulation controller
    Singleton Pattern
    A note on patterns: http://stackoverflow.com/questions/1318406/why-is-the-borg-pattern-better-than-the-singleton-pattern-in-python
    """
    __single = None
    __time = None
    __gui = None
    __object_list = None
    __update_list = None
    run_done = None

    def __init__(self, _gui=True):
        if not Simulator.__single:
            Simulator.__time = sim_time.Time()
            Simulator.__object_list = []
            Simulator.__update_list = []
            if _gui:
                import gui
                Simulator.__gui = gui.GUI(Simulator.__time)
            Simulator.__single = self
        else:
            raise RuntimeError('A Simulator already exists')

    @classmethod
    def get_instance(cls):
        if not cls.__single:
            cls.__single = Simulator()
        return cls.__single

    @classmethod
    def time(cls):
        return cls.__time

    @classmethod
    def gui(cls):
        if cls.__gui is None:
            import gui
            Simulator.__gui = gui.GUI(Simulator.__time)
        return cls.__gui

    @classmethod
    def object_list(cls, add=None):
        if add is not None:
            cls.__object_list.append(add)
        return cls.__object_list

    @classmethod
    def run(cls, stop: float = None, dt: float = None, plot_update_interval: float = 100,
            data_collect_interval: float = None, block_after=True):
        """
        Run a time-based simulation.
        Each time-registered object is moved forward by dt
        :param stop:
        :param dt:
        :param plot_update_interval: frequency to update graphs (in ms)
        :param data_collect_interval: frequency to collect data for plotting (in ms)
        :param block_after: does gui cause a pause/block after run is finished. If False, graphs close immediately upon
        completion (default: True)
        """
        if stop is None:
            stop = cls.__time.stop
        if dt is None:
            dt = cls.__time.dt
        if data_collect_interval is None:
            data_collect_interval = dt
        if plot_update_interval < data_collect_interval:
            data_collect_interval = plot_update_interval
        print("run from {0} until {1} with time step of {2} ".format(0, stop, dt))
        cls.run_done = False
        cls.__time.reset()
        cls.clear_graphs()
        time.clock()
        for t in range(1, int(round(stop / dt)) + 1):
            cls.__clear_updates()
            if t % (data_collect_interval / dt) == 0:
                cls.update_graphs()
            if t % (plot_update_interval / dt) == 0:
                cls.plot_graphs()
            for compartment in cls.__object_list:
                compartment.step(cls.__time)
            cls.__time.step(dt)
            cls.__apply_updates()
        cls.run_done = True
        cls.plot_graphs()
        print("time taken: {}".format(time.clock()))
        if block_after and cls.__gui is not None:
            cls.__gui.block()

    @classmethod
    def to_update(cls, obj, var, value, update_type: UpdateType):
        """
        Stores the value change for a var to be applied at the end of the time step.

        :param obj: object that the variable is a member of
        :param var: variable of the object to be updated
        :param value: the value to be updated at the end of the time step
        :param update_type: the type of update to apply to the variable
        """
        cls.__update_list.append(DeferredUpdate(obj, var, value, update_type))

    @classmethod
    def to_update_multi(cls, obj, d: dict):
        for var, sub_dict in d.items():
            cls.to_update(obj, var, sub_dict["value"], sub_dict["type"])

    @classmethod
    def to_update_change(cls, obj, var, delta_value):
        """
        Stores the value change for a var to be applied at the end of the time step.

        :param obj: object that the variable is a member of
        :param var: variable of the object to be updated
        :param delta_value: the change in value to be updated at the end of the time step
        """
        cls.__update_list.append(DeferredUpdate(obj, var, delta_value, UpdateType.CHANGE))

    @classmethod
    def to_update_set(cls, obj, var, value):
        """
        Stores the value for a var in a dictionary to be applied at the end of the time step.
        :param obj: object that the variable is a member of
        :param var: variable of the object to be set
        :param value: the value to be set to at the end of the time step
        """
        cls.__update_list.append(DeferredUpdate(obj, var, value, UpdateType.SET))

    @classmethod
    def __clear_updates(cls):
        cls.__update_list = []

    @classmethod
    def __apply_updates(cls):
        for deferred_update in cls.__update_list:
            deferred_update.apply_update()
        # for obj, var_dict in cls.__update_list.items():
        #     for var, delta_value in var_dict.items():
        #         obj[var] += delta_value

    @classmethod
    def clear_graphs(cls):
        if cls.__gui is not None:
            for graph in cls.__gui.graph_list():
                graph.clear()

    @classmethod
    def update_graphs(cls):
        if cls.run_done is False:
            if cls.__gui is not None:
                for graph in cls.__gui.graph_list():
                    graph.update()

    @classmethod
    def plot_graphs(cls):
        if cls.__gui is not None:
            for graph in cls.__gui.graph_list():
                graph.plot_graph()

    @classmethod
    def register_compartment(cls, compartment):
        """
        Add compartment to list of compartments to be updated at each time step
        :param compartment:
        :return:
        :raise TypeError if compartment not an instance of Compartment
        """
        if isinstance(compartment, sim_time.TimeMixin):
            cls.__object_list.append(compartment)
        else:
            raise TypeError("Compartment instance expected {0} given".format(type(compartment)))

    @classmethod
    def dispose(cls):
        cls.__single = None
        cls.__time = None
        cls.__gui = None
        cls.__object_list = None
        cls.__update_list = None
