# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from graph import Graph


class GUI(object):
    """
    Instantiates a GUI
    Unique Pattern
    A note on patterns: http://stackoverflow.com/questions/1318406/why-is-the-borg-pattern-better-than-the-singleton-pattern-in-python
    """
    # list of graphs
    __graph_list = []
    # simulation time object reference
    __time = None

    def __init__(self):
        raise SyntaxError("GUI called using __init__ instead of init")

    @classmethod
    def init(cls, _time):
        """
        Instantiates a new GUI, or overwrites _time, and makes graphics interactive (non-blocking)
        :param _time: simulation time object
        :return: class object

        Usage:
        gui = GUI.init()
        """
        GUI.__time = _time
        plt.ion()
        return cls

    @classmethod
    def __graphs(cls):
        """
        Get all graphs in GUI
        :return: graph list
        """
        return cls.__graph_list

    @classmethod
    def add_graph(cls):
        """
        Add Graph object to graph list
        :return:
        """
        g = Graph(cls.__time)
        GUI.__graph_list.append(g)
        return g

    @classmethod
    def clear_graphs(cls):
        """
        Call all GUI's graphs to clear their contents
        """
        for graph in cls.__graph_list:
            graph.clear()

    @classmethod
    def close_graphs(cls):
        """
        Close all GUI's graph's
        """
        plt.close('all')
        cls.__graph_list = []

    @classmethod
    def update_graphs(cls):
        """
        Call all GUI's graphs to update their values (does not mean plot)
        """
        for graph in cls.__graph_list:
            graph.update()

    @classmethod
    def plot_graphs(cls):
        """
        Call all GUI's graphs to plot their contents
        """
        for graph in cls.__graph_list:
            graph.plot_graph()

    @classmethod
    def block(cls, block=True):
        plt.show(block=block)


# generator methods for class methods
new_graph = GUI.add_graph
