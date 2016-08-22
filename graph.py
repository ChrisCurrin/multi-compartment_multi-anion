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
    def __init__(self):
        plt.figure()
        plt.plot([], [])
        self.follow_list = []

    def graph(self, time, K, Na, Cl, X, Vm, W):
        plt.subplot(2, 1, 1)
        plt.plot(time, K, '-c', time, Na, '-r', time, Cl, '-g', time, X, '-b', time, Vm, '--')
        plt.legend(['E_K', 'E_Na', 'E_Cl', 'E_X', 'V_m'])
        plt.subplot(2, 1, 2)
        plt.plot(time, W, label='relative volume')
        plt.legend()
        plt.show()

    def add_var(self, x_object, x_var, y_object, y_var):
        self.follow_list.append(((x_object, x_var), (y_object, y_var)))

    def update(self):
        for i, (x_tuple, y_tuple) in enumerate(self.follow_list):
            (x_object, x_var) = x_tuple
            (y_object, y_var) = y_tuple
            x = x_object[x_var]
            y = y_object[y_var]
            plt.gca().lines[i].set_xdata(x)
            plt.gca().lines[i].set_ydata(y)
            plt.gca().relim()
            plt.gca().autoscale_view()
            plt.pause(0.05)

