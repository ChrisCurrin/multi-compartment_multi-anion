# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
import matplotlib.pyplot as plt


class Graph:
    """
    Displays a graph for plotting of variables
    """

    def __init__(self, _time):
        self.time = _time
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        self.ax = self.fig.add_subplot(111)
        self.ax.hold()
        plt.hold()
        self.follow_list = []

    def add_var(self, x_object: any, x_var: str, y_object: any, y_var: str, line_style: str = None, units_scale: float = None, plot_units:str = None):
        try:
            x_object[x_var]
            y_object[y_var]
        except KeyError:
            print("variable {} not present in {}".format(x_var, x_object))
        else:
            if line_style is None:
                line, = self.ax.plot([], [], label=".".join([y_object.name, y_var]))
            else:
                line, = self.ax.plot([], [], line_style, label=".".join([y_object.name, y_var]))
            if units_scale is None:
                units_scale = 1
            self.follow_list.append(((x_object, x_var, []), (y_object, y_var, [], units_scale), line))
            self.ax.legend()
            self.update()

    def add_voltage(self, y_object: any, **kwargs):
        self.add_var(self.time, "time", y_object, "V", **kwargs)

    def add_ion_conc(self, y_object: any, ion: str, **kwargs):
        self.add_var(self.time, "time", y_object, ion, **kwargs)

    def clear(self):
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data, units_scale) = y_tuple
            self.follow_list[i] = ((x_object, x_var, []), (y_object, y_var, [], units_scale), line)

    def update(self):
        """
        For each variable tracked, place the object's variable value in a list.
        The object must contain the variable of interest and implement:

        def __getitem__(self, item):
            return self.__dict__[item]

        """
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data, units_scale) = y_tuple
            x_data.append(x_object[x_var])
            y_data.append(y_object[y_var]*units_scale)

    def plot_graph(self):
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data, units_scale) = y_tuple
            line.set_xdata(x_data)
            line.set_ydata(y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        plt.pause(0.001)

    def handle_close(self, evt):
        print('Closed Figure!')
