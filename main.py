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
    dt = 0.001
    comp = Compartment("soma", pkcc2=0, z=-0.85)

    v = gui.add_graph()
    v.add_voltage(comp, line_style='k', units_scale=1000, plot_units='mV')  # black
    g = gui.add_graph()
    g.add_ion_conc(comp, "cli", line_style='g')  # green
    g.add_ion_conc(comp, "ki", line_style='c')  # cyan
    g.add_ion_conc(comp, "nai", line_style='r')  # red
    g.add_ion_conc(comp, "xi", line_style='b')  # blue

    # find steady-state values of ions
    sim.run(stop=500, dt=0.001, plot_update_interval=150, data_collect_interval=10, block_after=False)

    # values from steady-state
    # comp.cli=0.015292947537423218
    # comp.ki=0.023836660428807395
    # comp.nai=0.1135388427892471
    # comp.xi=0.14364453159746354
    # soma.cli:0.015294296950162089
    # soma.ki:0.02383445376161132
    # soma.nai:0.11354115831823093
    # soma.xi:0.14364307332293696
    print("Ion concentrations")
    for ion in ["cli", "ki", "nai", "xi"]:
        print("{}.{}:{}".format(comp.name, ion, comp[ion]))

    comp2 = comp.copy("dendrite")
    # change ion concentration
    comp2.cli = comp2.cli - 1e-3
    comp2.ki = comp2.ki - 1e-3
    #comp.cli = 0.05

    # set diffusion value
    D = 1  # um2/ms
    D = D * 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
    # create diffusion connection
    diffusion_object = Diffusion(comp, comp2, ions=['cli'], D=D)

    print(diffusion_object.dx)
    print(diffusion_object.ficks_law("cli", D=D)*dt/diffusion_object.dx)   # (M * dm) to (mM * um) per ms
    print("Ion concentrations")
    for ion in ["cli", "ki", "nai", "xi"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))
    v.add_voltage(comp2, line_style='--k', units_scale=1000, plot_units='mV')  # black
    g.add_ion_conc(comp2, "cli", line_style='--g')  # green
    g.add_ion_conc(comp2, "ki", line_style='--c')  # cyan
    g.add_ion_conc(comp2, "nai", line_style='--r')  # red
    g.add_ion_conc(comp2, "xi", line_style='--b')  # blue

    sim.run(stop=1, dt=dt, plot_update_interval=dt, data_collect_interval=dt)
    #sim.run(stop=50, dt=dt, plot_update_interval=5, data_collect_interval=0.025)
    print("Ion concentrations")
    for ion in ["cli", "ki", "nai", "xi"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))


if __name__ == "__main__":
    main()
