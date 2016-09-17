# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""
import numpy as np
from constants import F
from common import RTF
from common import default_radius, default_length, \
    clo, ko, nao, xo_z, oso, \
    default_p, \
    gk, gna, gcl, \
    ck, cna
from sim_time import TimeMixin, Time
import simulator
import time


class Compartment(TimeMixin):
    """

    """

    def __init__(self, name, radius=default_radius, length=default_length, pkcc2=0, z=-0.85, nai=50e-3, ki=80e-3, p=default_p, cli=0):
        self.unique_id = str(time.time())
        self.name = name
        self.r = radius  # in um
        self.L = length  # in um
        self.pkcc2 = pkcc2  # strength of kcc2
        self.z = z  # intracellular charge of impermeant anions
        self.w = np.pi * self.r ** 2 * self.L  # initial volume in liters
        self.Ar = 4e6  # area constant (F and H method)
        self.C = 7e-6  # capacitance (F/dm^2)
        # (F/C*area scaling constant)
        self.FinvCAr = F / (self.C * self.Ar)
        # na,k,cl,x: intracellular starting concentrations
        self.nai = nai
        self.ki = ki
        self.cli = ((oso-self.nai-self.ki)*self.z+self.nai+self.ki)/(1+self.z)
        self.xi = (self.cli - self.ki - self.nai) / self.z
        if self.xi < 0 or self.cli < 0:
            raise RuntimeError("Initial choice of either ki or nai resulted in negative concentration of intracellular ion - choose different starting values.")
        # intracellular osmolarity
        self.osi = self.nai + self.ki + self.cli + self.xi
        if self.osi != oso:
            print("Compartment not osmo-neutral")
        self.nao = nao
        self.ko = ko
        self.clo = clo
        # define step attributes for t=0

        # define constant element of pump rate
        self.p = p
        # voltage
        self.V = self.FinvCAr * (self.nai + (self.ki + (self.z * self.xi) - self.cli))
        # pump rate
        self.jp = self.p * (self.nai / nao) ** 3

        # register component with simulator
        simulator.Simulator.get_instance().register_compartment(self)

    def step(self, _time: Time = None):
        """
        perform a time step for the compartment
        1) update voltage (V)
        2) update cubic pump rate
        3) update KCC2 flux rate
        4) solve ionic flux equations for t+dt from t
        5) increment ionic concentrations
        6) update volume
        7) correct ionic concentrations due to volume change
        :param _time: time object for reference
        """
        if _time is None:
            raise ValueError("{} has no time object specified".format(self.__class__.__name__))
        # update voltage
        self.V = self.FinvCAr * (self.nai + self.ki - self.cli + self.z * self.xi)
        # update cubic pump rate (dependent on sodium gradient)
        self.jp = self.p * (self.nai / self.nao) ** 3
        # kcc2
        self.jkcc2 = (gk * self.pkcc2 * (self.ki * self.clo - self.ki * self.cli))  # Fraser and Huang
        # jkcc2=sw*gk*pkcc*(K[ctr-2]-Cl[ctr-2])/10000.0 #Doyon

        # ionic flux equations
        # dnai,dki,dcli: increase in intracellular ion conc during time step dt
        dnai = -_time.dt * self.Ar * (gna * (self.V - RTF * np.log(self.nao / self.nai)) + cna * self.jp)
        dki = -_time.dt * self.Ar * (gk * (self.V - RTF * np.log(self.ko / self.ki)) - ck * self.jp + self.jkcc2)
        dcli = _time.dt * self.Ar * (gcl * (self.V + RTF * np.log(self.clo / self.cli)) - self.jkcc2)

        # increment concentrations
        # self.nai += dna
        # self.ki += dk
        # self.cli += dcl
        UpdateType = simulator.UpdateType
        simulator.Simulator.get_instance().to_update_multi(self, {
            'nai': {
                "value": dnai,
                "type": UpdateType.CHANGE
            }, 'ki': {
                "value": dki,
                "type": UpdateType.CHANGE
            }, 'cli': {
                "value": dcli,
                "type": UpdateType.CHANGE
            }
        })

        simulator.Simulator.get_instance().to_update(self, self.name, self.update_values, UpdateType.FUNCTION)

    def update_values(self):
        # intracellular osmolarity
        self.osi = self.nai + self.ki + self.cli + self.xi
        # update volume
        self.osi = self.nai + self.ki + self.cli + self.xi  # intracellular osmolarity
        w2 = (self.w * self.osi) / oso  # update volume

        # correct ionic concentrations by volume change
        self.nai = (self.nai * self.w) / w2
        self.ki = (self.ki * self.w) / w2
        self.cli = (self.cli * self.w) / w2
        self.xi = (self.xi * self.w) / w2
        self.w = w2
        # affect volume change into length change
        self.L = self.w / (np.pi * self.r ** 2)

    def copy(self, name):
        """
        Create a new Compartment identical to this one
        :param name: identifier for the new compartment
        :return: new Compartment
        """
        comp = Compartment(name, radius=self.r, length=self.L, pkcc2=self.pkcc2, z=self.z, nai=self.nai, ki=self.ki,
                           cli=self.cli, p=self.p)
        comp.xi = self.xi
        # intracellular osmolarity
        comp.osi = comp.nai + comp.ki + comp.cli + comp.xi
        # extracellular osmo (fixed)
        comp.oso = comp.osi
        comp.xo = comp.oso - clo - ko - nao
        comp.nao = nao
        comp.ko = ko
        comp.clo = clo
        # extracellular concentration of impermeants (here w/ zo=-1)
        comp.V = comp.FinvCAr * (comp.nai + (comp.ki + (comp.z * comp.xi) - comp.cli))
        # pump rate
        return comp

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __str__(self, *args, **kwargs):
        return self.name
