# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
# permeabilities
gna = 3e-9
gk = 5e-8
gcl = 5e-8  # gna,gk,gcl: conductances in mS/cm^2 conv to S/dm^2 (10^-3/10^-2) - corrected for neuron
# stochiometries
ck = 2
cna = 3  # cna,ck: pump (ATPase) stoichiometries
# pump rates
p = 1e-3
# concentrations
nao = 138e-3
clo = 119e-3
ko = 2.8e-3  # nao,clo,ko: extracellular concentrations (mM converted to M)
# KCC2 strength
pkcc = 1.0

# DEFAULT cell dimensions
default_radius = 5 * 1e-5  # radius in um convert to dm
default_length = 100 * 1e-5  # length in um converted to dm

n = 200  # points to plot