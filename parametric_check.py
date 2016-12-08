# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""

import numpy as np
from constants import F
from common import clo, ko, nao, gk, gna, gcl, oso, RTF
from simulator import Simulator
from compartment import Compartment
import time
import matplotlib.pyplot as plt
import gui


def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step

def zplm(z, gkcc, ose):
    P = frange(-8.0, -4.5, 0.001)
    beta = 1.0 / (gk * gcl + gkcc * gcl + gk * gkcc)
    nai = []
    ki = []
    cli = []
    xi = []
    vm = []
    pi = []

    for p in P:
        q = 10 ** (p) / (F * RTF)
        if z == -1:
            theta = 0.5 * ose / (nao * np.exp(-3 * q / gna) + ko * np.exp(2 * q * (gcl + gkcc) * beta))
        else:
            theta = (-z * ose + np.sqrt(z ** 2 * ose ** 2 + 4 * (1 - z ** 2) * clo * np.exp(-2 * q * gkcc * beta) * (
                nao * np.exp(-3 * q / gna) + ko * np.exp(2 * q * (gcl + gkcc) * beta)))) / (
                        2 * (1 - z) * (nao * np.exp(-3 * q / gna) + ko * np.exp(2 * q * (gcl + gkcc) * beta)))
        v = (-np.log(theta)) * RTF
        vm.append(v)
        nai.append(nao * np.exp(-v / RTF - 3 * q / gna))
        ki.append(ko * np.exp(-v / RTF + 2 * q * (gcl + gkcc) * beta))
        cli.append(clo * np.exp(+v / RTF - 2 * q * gkcc * beta))
        xi.append(ose - nai[-1] - cli[-1] - ki[-1])
        pi.append(np.log10(F * RTF * q / (((nao * np.exp(-v / RTF - 3 * q / gna)) / nao) ** 3)))

    return pi, nai, ki, cli, xi, vm


def checkpara(kcc2=1e-8, z=-0.85):
    ti = [[], [], [], [], []]
    T = [-8.0, -7.0, -6.0, -5.5, -5.0, -4.5, -4, -3.5, -3.0, -2.0]
    sim = Simulator()

    for k in T:
        q = 10 ** (k) / F
        comp = Compartment("soma with pump rate 1e" + str(k) + "/F", pkcc2=kcc2, z=z, p=q)
        time.clock()
        sim.run(continuefor=1000, plot_update_interval=5000,block_after=False)
        ti[0].append(comp.V)
        ti[1].append(comp.ki)
        ti[2].append(comp.nai)
        ti[3].append(comp.cli)
        ti[4].append(comp.xi)

    para = zplm(z, kcc2, oso)

    return T, ti, para

T, ti, para = checkpara()
plt.figure()
plt.plot(para[0], para[1], 'r', para[0], para[2], 'c', para[0], para[3], 'g', para[0], para[4], 'b', para[0],
         para[5], 'k', T, ti[0], 'ok', T, ti[1], 'oc', T, ti[2], 'or', T, ti[3], 'og', T, ti[4], 'ob')
plt.title(
    'parametric plot vs time series runs: ion concentrations and membrane potential over log(cubic pump rate)')
plt.xlabel('log(F.pump rate)')
plt.ylabel('mV')
plt.savefig('fig.eps')
plt.show()
