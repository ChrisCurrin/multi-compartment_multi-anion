# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""
import matplotlib.pyplot as plt
import numpy as np

class Graph(object):
    """
    Displays a graph for plotting of variables
    """

    def __init__(self, _time):
        self.time = _time
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        self.ax = self.fig.add_subplot(111)
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        self.follow_list = []
        self.fig.canvas.draw()

    def add_var(self, x_object: any, x_var: str or dict, y_object: any, y_var: str or dict, line_style: str = None,
                y_units_scale: float = 1.0, y_plot_units: str = None):
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
            # these blocks check if the object is hashable and has the variable wanting to be plotted
            # if the variable is a dictionary of multiple entries, each entry is treated as a variable
            if isinstance(x_var, str):
                assert x_object[x_var] or x_object[x_var] == 0
            elif isinstance(x_var, dict):
                if len(x_var) > 1:
                    for (key, val) in x_var.items():
                        self.add_var(x_object, {key: val}, y_object, y_var, line_style, y_units_scale, y_plot_units)
                else:
                    for (key, val) in y_var.items():
                        assert y_object[key][val] or y_object[key][val] == 0
            else:
                assert False
            if isinstance(y_var, str):
                assert y_object[y_var] or y_object[y_var] == 0
            elif isinstance(y_var, dict):
                if len(y_var) > 1:
                    for (key, val) in y_var.items():
                        self.add_var(x_object, x_var, y_object, {key: val}, line_style, y_units_scale, y_plot_units)
                else:
                    for (key, val) in y_var.items():
                        assert y_object[key][val] or y_object[key][val] == 0
            else:
                assert False
        except KeyError as keyerror:
            print("{}: variable {} or {} not present in {} or {}".format(keyerror, x_var, y_var, x_object, y_object))
        else:
            if isinstance(y_var, str):
                label = ".".join([y_object.name, y_var])
            elif isinstance(y_var, dict):
                for (key, val) in y_var.items():
                    label = ".".join([y_object.name, key, val])
            else:
                label = "ERROR"
            # plot
            if line_style is None:
                line, = self.ax.plot([], [], label=label)
            else:
                line, = self.ax.plot([], [], line_style, label=label)
            plt.pause(0.000001)
            # store
            self.follow_list.append(
                ((x_object, x_var, np.array([], dtype=np.float64)),
                (y_object, y_var, np.array([], dtype=np.float64), y_units_scale),
                line))
            # self.follow_list.append(((x_object, x_var, []), (y_object, y_var, [], y_units_scale), line))
            # auto-legend
            self.ax.legend(loc=3)
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

    def add_ion_conc(self, y_object: any, ion: str or dict, **kwargs):
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
            self.follow_list[i] = ((x_object, x_var, np.array([], dtype=np.float64)),
                                   (y_object, y_var, np.array([], dtype=np.float64), units_scale), line)

    def update(self):
        """
        Get the values for x-var and y-var from their respective objects for future plotting.
        """
        for i, (x_tuple, y_tuple, line) in enumerate(self.follow_list):
            (x_object, x_var, x_data) = x_tuple
            (y_object, y_var, y_data, units_scale) = y_tuple
            if isinstance(x_var, str):
                x_data = np.append(x_data,x_object[x_var])
            elif isinstance(x_var, dict):
                for (key, val) in x_var.items():
                    x_data = np.append(x_data,x_object[key][val])
            if isinstance(y_var, str):
                y_data = np.append(y_data,y_object[y_var] * units_scale)
            elif isinstance(y_var, dict):
                for (key, val) in y_var.items():
                    y_data = np.append(y_data,y_object[key][val] * units_scale)
            # replace object at index i
            self.follow_list[i] = ((x_object, x_var, x_data),
                                   (y_object, y_var, y_data, units_scale),
                                    line)

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
            self.fig.canvas.restore_region(self.background)
            # redraw just the points
            self.ax.draw_artist(line)
            # fill in the axes rectangle
            self.fig.canvas.blit(self.ax.bbox)
        self.ax.relim()
        self.ax.autoscale_view()
        plt.pause(0.00001)

    def handle_close(self, evt):
        """
        Custom close event handler
        :param evt:
        """
        print('Closed Figure!')

    def save(self, name):
        self.fig.savefig(name)
        
    def show(self):
        plt.show()
