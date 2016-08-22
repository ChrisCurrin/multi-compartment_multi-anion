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
        Unique Pattern
        A note on patterns: http://stackoverflow.com/questions/1318406/why-is-the-borg-pattern-better-than-the-singleton-pattern-in-python
        """
    t = None
    dt = None
    stop = None

    @classmethod
    def __init__(cls, _t=0, _dt=1e-3, stop=5.0):
        Time.t = _t
        Time.dt = _dt
        Time.stop = stop

    @classmethod
    def step(cls):
        """
        Moves forward one time step
        :return:
        """
        Time.t += Time.dt
