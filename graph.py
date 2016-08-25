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
        plt.ion()
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        self.ax = self.fig.add_subplot(111)
        plt.hold()
        plt.show(block=False)
        self.follow_list = []

    def add_var(self, x_object: any, x_var: str, y_object: any, y_var: str, line_style: str = None):
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
            self.follow_list.append(((x_object, x_var, []), (y_object, y_var, []), line))
            self.ax.legend()
            self.update()

    def add_voltage(self, y_object: any, line_style: str = None):
        self.add_var(self.time, "time", y_object, "V", line_style=line_style)

    def add_ion_conc(self, y_object: any, ion: str, line_style: str = None):
        self.add_var(self.time, "time", y_object, ion, line_style=line_style)

    def clear(self):
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data) = y_tuple
            self.follow_list[i] = ((x_object, x_var, []), (y_object, y_var, []), line)

    def update(self):
        """
        For each variable tracked, place the object's variable value in a list.
        The object must contain the variable of interest and implement:

        def __getitem__(self, item):
            return self.__dict__[item]

        """
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data) = y_tuple
            x_data.append(x_object[x_var])
            y_data.append(y_object[y_var])

    def plot_graph(self):
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data) = y_tuple
            line.set_xdata(x_data)
            line.set_ydata(y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        plt.pause(0.001)

    def handle_close(self, evt):
        print('Closed Figure!')
