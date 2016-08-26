# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
from simulator import Simulator
from compartment import Compartment
from diffusion import Diffusion


def main():
    print("main")
    sim = Simulator()
    gui = sim.gui()
    t = sim.time()
    comp = Compartment("soma", kcc2=0, z=-0.85)
    comp2 = Compartment("dendrite", kcc2=1, z=-0.85)
    comp2.cli = 0.1
    diffusion_object = Diffusion(comp, comp2, 'cli', 1)
    print(comp.cli)
    v = gui.add_graph()
    v.add_voltage(comp, 'k')  # black
    v.add_voltage(comp2, '-k')  # black
    g = gui.add_graph()
    g.add_ion_conc(comp, "cli", 'g')  # green
    g.add_ion_conc(comp, "ki", 'c')  # cyan
    g.add_ion_conc(comp, "nai", 'r')  # red
    g.add_ion_conc(comp, "xi", 'b')  # blue
    g.add_ion_conc(comp2, "cli", '--g')  # green
    g.add_ion_conc(comp2, "ki", '--c')  # cyan
    g.add_ion_conc(comp2, "nai", '--r')  # red
    g.add_ion_conc(comp2, "xi", '--b')  # blue

    sim.run(stop=500, dt=0.001, plot_update_interval=100, data_collect_interval=0.1)


if __name__ == "__main__":
    main()
