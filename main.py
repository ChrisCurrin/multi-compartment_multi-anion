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

    comp = Compartment("soma", kcc2=0, z=-0.85, nai=0.1143, ki=0.0229, cli=0.01321)

    v = gui.add_graph()
    v.add_voltage(comp, line_style='k', units_scale=1000, plot_units='mV')  # black
    g = gui.add_graph()
    g.add_ion_conc(comp, "cli", line_style='g')  # green
    g.add_ion_conc(comp, "ki", line_style='c')  # cyan
    g.add_ion_conc(comp, "nai", line_style='r')  # red
    g.add_ion_conc(comp, "xi", line_style='b')  # blue

    # find steady-state values of ions
    # sim.run(stop=1000, dt=0.001, plot_update_interval=150, data_collect_interval=10, block_after=False)

    comp2 = comp.copy("dendrite")
    comp2.cli = 0.10
    comp.cli = 0.01
    D = 1               # um2/ms
    D = (D*1e-5) ** 2   # um2 to dm2 (D in dm2/ms)
    diffusion_object = Diffusion(comp, comp2, ion='cli', D=D)
    print(diffusion_object.dx)
    print(diffusion_object.ficks_law("cli", D=D)*1e8/diffusion_object.dx)   # (M * dm) to (mM * um) per ms
    for ion in ["cli", "ki", "nai", "xi"]:
        print(ion)
        print("{}:{} \t {}:{}".format(comp.name, comp[ion], comp2.name, comp2[ion]))
    v.add_voltage(comp2, line_style='--k', units_scale=1000, plot_units='mV')  # black
    g.add_ion_conc(comp2, "cli", line_style='--g')  # green
    g.add_ion_conc(comp2, "ki", line_style='--c')  # cyan
    g.add_ion_conc(comp2, "nai", line_style='--r')  # red
    g.add_ion_conc(comp2, "xi", line_style='--b')  # blue

    sim.run(stop=0.01, dt=0.001, plot_update_interval=1, data_collect_interval=0.001)
    for ion in ["cli", "ki", "nai", "xi"]:
        print(ion)
        print("{}:{} \t {}:{}".format(comp.name, comp[ion], comp2.name, comp2[ion]))


if __name__ == "__main__":
    main()
