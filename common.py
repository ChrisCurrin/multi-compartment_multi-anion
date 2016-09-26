# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""
from constants import F, R

T = 25 + 273.15
RTF = R*T / F
# permeabilities
gna = 5e-9
gk = 5e-8
gcl = 1e-8  # gna,gk,gcl: conductances in mS/cm^2 conv to S/dm^2 (10^-3/10^-2) - corrected for neuron
# stochiometries
ck = 2
cna = 3  # cna,ck: pump (ATPase) stoichiometries
# pump rates
default_p = 1e-2 / F
# concentrations
nao = 145e-3
clo = 119e-3
ko = 3.5e-3
xo = -1.0*(clo-nao-ko) # nao,clo,ko,xo: extracellular concentrations (mM converted to M)
xo_z = xo/2.0
oso = xo + nao + clo + ko
# KCC2 strength
pkcc = 1.0

# DEFAULT cell dimensions
default_radius = 5 * 1e-5  # radius in um convert to dm
default_length = 100 * 1e-5  # length in um converted to dm

n = 200  # points to plot
