# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""
from constants import F, R

T = 37 + 273.15
RTF = R * T / F
RT = R * T
# permeabilities
gna = 2e-3/F
gk = 7e-3/F
gcl = 2e-3/F  # gna,gk,gcl: conductances in mS/cm^2 conv to S/dm^2 (10^-3/10^-2) - corrected for neuron
# stochiometries
ck = 2
cna = 3  # cna,ck: pump (ATPase) stoichiometries
# pump rates
default_p = 0.1 / F
# concentrations
nao = 145e-3
clo = 119e-3
ko = 3.5e-3
xo = -1.0 * (clo - nao - ko)  # nao,clo,ko,xo: extracellular concentrations (mM converted to M)
xo_z = xo * 0.02
oso = xo + nao + clo + ko

# DEFAULT cell dimensions
default_radius = 5 * 1e-5  # radius in um convert to dm
default_length = 100 * 1e-5  # length in um converted to dm

default_radius_short = 0.5 * 1e-5  # radius in um convert to dm
default_length_short = 100 * 1e-5  # length in um converted to dm

points_to_plot = 200  # points to plot

vw = 0.018 #partial molar volume of water, dm3/mol
pw = 0.0015 #osmotic permeability, biological membrane (muscle? unknown), dm s
km=5*10**(-14) #extensional rigidity of RBC at 23 deg, Mohandas and Evans (1994), N/dm