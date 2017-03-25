# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris & Kira
"""
# constants
# R with different units
# 8.31451                   J K-1 mol-1
# 8.20578 x 10-2            L atm K-1 mol-1
# 8.31451 x 10-2                L bar K-1 mol-1
# 8.31451                           Pa m3 K-1 mol-1
# 62.364                             L Torr K-1 mol-1
# 1.98722                           cal K-1 mol-1

R = 8.31446
F = 96485.33  # Faraday's constant        C mol-1
k = 1.38e-23  # Boltzmann constant        J K-1
q = 1.602176620898e-19  # elementary charge         C
Na = 6.022e23  # Avogadro's constant       mol-1


def valence(ion: str):
    ion = ion.lower()
    if ion.endswith("i") or ion.endswith("o"):
        ion = ion[:-1]
    return {"cl": -1, "k": 1, "na": 1}[ion]
