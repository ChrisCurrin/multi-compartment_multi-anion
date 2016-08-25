# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
import numpy as np
from constants import F, R
from common import default_radius, default_length, \
    clo, ko, nao, \
    p, pkcc, \
    gk, gna, gcl, \
    ck, cna
from sim_time import TimeMixin
import simulator


class Compartment(TimeMixin):
    """

    """

    def __init__(self, name, radius=default_radius, length=default_length, kcc2=0, z=-1):
        self.name = name
        self.r = radius  # in um
        self.L = length  # in um
        self.gkcc = kcc2  # strength of kcc2
        self.z = z  # intracellular charge of impermeant anions
        self.w = np.pi * self.r ** 2 * self.L  # initial volume in liters
        self.Ar = 4e6  # area constant (F and H method)
        self.C = 7e-6  # capacitance (F/dm^2)
        # (F/C*area scaling constant)
        self.FinvCAr = F / (self.C * self.Ar)
        self.nai = 140e-3
        self.ki = 2.5e-3
        self.cli = 78.3931e-3
        # na,k,cl,x: intracellular starting concentrations
        self.xi = (self.cli - self.ki - self.nai) / self.z
        # intracellular osmolarity
        self.osi = self.nai + self.ki + self.cli + self.xi
        # extracellular osmo (fixed)
        self.oso = self.osi
        # extracellular concentration of impermeants (here w/ zo=-1)
        self.xo = self.oso - clo - ko - nao
        self.nao = nao
        self.ko = ko
        self.clo = clo
        # define step attributes for t=0

        # voltage
        self.V = self.FinvCAr * (self.nai + self.ki - self.cli + self.z * self.xi)
        # pump rate
        self.jp = p * (self.nai / nao) ** 3

        self.time = 0
        # register component with simulator
        simulator.Simulator.get_instance().register_compartment(self)

    def step(self, _dt: float = None):
        """
        perform a time step for the compartment
        1) update voltage (V)
        2) update cubic pump rate
        3) update KCC2 flux rate
        4) solve ionic flux equations for t+dt from t
        5) increment ionic concentrations
        6) update volume
        7) correct ionic concentrations due to volume change
        :param _dt: the change in time
        """
        if _dt is None:
            raise ValueError("{} has no timestep specified".format(self.__class__.__name__))
        # update voltage
        self.V = self.FinvCAr * (self.nai + self.ki - self.cli + self.z * self.xi)
        # update cubic pump rate (dependent on sodium gradient)
        self.jp = p * (self.nai / self.nao) ** 3
        # kcc2
        self.jkcc2 = (gk * pkcc * (self.ki * self.clo - self.ki * self.cli))  # Fraser and Huang
        # jkcc2=sw*gk*pkcc*(K[ctr-2]-Cl[ctr-2])/10000.0 #Doyon

        # ionic flux equations
        # dna,dk,dcl: increase in intracellular ion conc during time step dt
        dna = -_dt * self.Ar * (gna * (self.V - R * np.log(self.nao / self.nai)) + cna * self.jp)
        dk = -_dt * self.Ar * (gk * (self.V - R * np.log(self.ko / self.ki)) - ck * self.jp + self.jkcc2)
        dcl = _dt * self.Ar * (gcl * (self.V + R * np.log(self.clo / self.cli)) - self.jkcc2)

        # increment concentrations
        self.nai += dna
        self.ki += dk
        self.cli += dcl

        # update volume
        self.osi = self.nai + self.ki + self.cli + self.xi  # intracellular osmolarity
        w2 = (self.w * self.osi) / self.oso  # update volume

        # correct ionic concentrations by volume change
        self.nai = (self.nai * self.w) / w2
        self.ki = (self.ki * self.w) / w2
        self.cli = (self.cli * self.w) / w2
        self.xi = (self.xi * self.w) / w2
        self.w = w2
        self.time += _dt
        # print(self.V)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __str__(self, *args, **kwargs):
        return "Compartment: " + str(self.__dict__)
