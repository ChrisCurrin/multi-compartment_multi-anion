# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
from abc import ABCMeta, abstractmethod
import numpy as np

class TimeMixin(metaclass=ABCMeta):
    @abstractmethod
    def step(self):
        pass


class Time(TimeMixin):
    """
    Instantiates a Time control
    Borg Pattern
    A note on patterns: http://stackoverflow.com/questions/1318406/why-is-the-borg-pattern-better-than-the-singleton-pattern-in-python
    """
    __monostate = None

    def __init__(self, t=0.0, dt=1e-3, stop=5.0):
        """

        :param t: s
        :param dt: s
        :param stop:
        """
        if not Time.__monostate:
            Time.__monostate = self.__dict__
            # Your definitions here
            self.time = np.float64(t)
            self.dt = np.float64(dt)
            self.stop = np.float64(stop)
        else:
            self.__dict__ = Time.__monostate

    def step(self):
        """
        Moves forward one time step
        """
        self.time += self.dt

    def stepsize(self, dt=None):
        """
        Set the step size for each movement of time forward
        :param dt: change in time aka timestep size 
        """
        if dt is not None:
            self.dt = np.float64(dt)
        return self.dt

    def reset(self):
        self.time = np.float64(0.0)

    def __getitem__(self, item):
        return self.__dict__[item]
