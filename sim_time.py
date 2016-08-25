# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
from abc import ABCMeta, abstractmethod


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

    def __init__(self, t=0, dt=1e-3, stop=5):
        if not Time.__monostate:
            Time.__monostate = self.__dict__
            # Your definitions here
            self.time = t
            self.dt = dt
            self.stop = stop
        else:
            self.__dict__ = Time.__monostate

    def step(self, dt=None):
        """
        Moves forward one time step
        :return:
        """
        if dt is None:
            dt = self.dt
        self.time += dt

    def reset(self):
        self.time = 0

    def __getitem__(self, item):
        return self.__dict__[item]
