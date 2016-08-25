# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""

from graph import Graph
import matplotlib.pyplot as plt


class GUI:
    """
    Instantiates a GUI
    Unique Pattern
    A note on patterns: http://stackoverflow.com/questions/1318406/why-is-the-borg-pattern-better-than-the-singleton-pattern-in-python
    """
    __graph_list = []
    __time = None

    @classmethod
    def __init__(cls, _time):
        GUI.__time = _time

    @classmethod
    def graph_list(cls):
        return cls.__graph_list

    @classmethod
    def add_graph(cls):
        g = Graph(cls.__time)
        GUI.__graph_list.append(g)
        return g

    @classmethod
    def block(cls, block=True):
        plt.show(block=block)

    @classmethod
    def init(cls):
        # Define any computation performed when assigning to a "new" object
        return cls


# generator methods for class methods
new_graph = GUI.add_graph
