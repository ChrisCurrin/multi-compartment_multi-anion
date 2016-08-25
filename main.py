# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
from simulator import Simulator
from compartment import Compartment
import time


def main():
    print("main")
    sim = Simulator()
    gui = sim.gui()
    t = sim.time()
    comp = Compartment("soma", kcc2=0, z=-0.85)
    print(comp.cli)
    v = gui.add_graph()
    v.add_voltage(comp, 'k')  # black
    g = gui.add_graph()
    g.add_ion_conc(comp, "cli", 'g')  # green
    g.add_ion_conc(comp, "ki", 'c')   # cyan
    g.add_ion_conc(comp, "nai", 'r')  # red
    g.add_ion_conc(comp, "xi", 'blue')  # blue
    time.clock()
    sim.run(stop=1000, plot_update_interval=100)


if __name__ == "__main__":
    main()
