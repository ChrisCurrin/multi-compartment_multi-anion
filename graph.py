# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
import matplotlib.pyplot as plt


class Graph(object):
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

    def add_var(self, x_object: any, x_var: str, y_object: any, y_var: str, line_style: str = None, y_units_scale: float = 1.0, y_plot_units:str = None):
        """
        Add variables to be plotted.
        For each variable tracked, place the object's variable value in a list.
        The object must contain the variable of interest and implement:
            def __getitem__(self, item):
                return self.__dict__[item]

        :param x_object: the object to which the variable on the x axis belongs
        :param x_var:    x-axis variable
        :param y_object: the object to which the variable on the y axis belongs
        :param y_var:    y-axis variable
        :param line_style: see help(plt.plot()) for line_style guidance
        :param y_units_scale: how much should the y-var be scaled?
        :param y_plot_units: what are the units of the y axis?
        :return: self, for chaining
        """
        try:
            assert x_object[x_var]
            assert y_object[y_var]
        except KeyError:
            print("variable {} or {} not present in {}".format(x_var, y_var, x_object))
        else:
            # plot
            if line_style is None:
                line, = self.ax.plot([], [], label=".".join([y_object.name, y_var]))
            else:
                line, = self.ax.plot([], [], line_style, label=".".join([y_object.name, y_var]))
            # store
            self.follow_list.append(((x_object, x_var, []), (y_object, y_var, [], y_units_scale), line))
            # auto-legend
            self.ax.legend()
            self.update()
        return self

    def add_voltage(self, y_object: any, **kwargs):
        """
        Helper method to add voltage versus time

        :param y_object: object to which voltage should be tracked
        :param kwargs: other arguments for add_var
        :return: add_var return value
        """
        return self.add_var(self.time, "time", y_object, "V", **kwargs)

    def add_ion_conc(self, y_object: any, ion: str, **kwargs):
        """
        Helper method to add ion versus time

        :param y_object: object to which ion should be tracked
        :param ion: ion to be tracked
        :param kwargs: other arguments for add_var
        :return: add_var return value
        """
        return self.add_var(self.time, "time", y_object, ion, **kwargs)

    def clear(self):
        """
        Clear the plot of all values, erasing history of x and y variables.
        """
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data, units_scale) = y_tuple
            self.follow_list[i] = ((x_object, x_var, []), (y_object, y_var, [], units_scale), line)

    def update(self):
        """
        Get the values for x-var and y-var from their respective objects for future plotting.
        """
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data, units_scale) = y_tuple
            x_data.append(x_object[x_var])
            y_data.append(y_object[y_var]*units_scale)

    def plot_graph(self):
        """
        Plot the graphs using data retrieved during update()
        Graph is automatically scaled.
        plt.pause(small_time_value) is necessary to have the change be visible
        """
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data, units_scale) = y_tuple
            line.set_xdata(x_data)
            line.set_ydata(y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        plt.pause(0.001)

    def handle_close(self, evt):
        """
        Custom close event handler
        :param evt:
        """
        print('Closed Figure!')
