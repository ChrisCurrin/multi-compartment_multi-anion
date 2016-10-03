# -*- coding: utf-8 -*-
"""
Created on Mon Oct 03 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""
from simulator import Simulator
from compartment import Compartment
from diffusion import Diffusion


def anions():
    print("main_anions")
    sim = Simulator()
    gui = sim.gui()
    dt = 0.001
    # comp = Compartment("soma", pkcc2=0, z=-0.85)
    comp = Compartment("soma", pkcc2=0, z=-0.85  # )
                       , cli=0.01819925284075134,
                       ki=0.019909567493822927,
                       nai=0.11094226350779378)

    # find steady-state values of ions
    sim.run(stop=50, dt=0.001, plot_update_interval=500, data_collect_interval=500, block_after=False)
    # values from steady-state
    # soma.cli:0.01819948776551597
    # soma.ki:0.019909327159644736
    # soma.nai:0.11094252293794836
    # soma.xi:0.13254866213689095

    v = gui.add_graph()
    v.add_voltage(comp, line_style='k', y_units_scale=1000, y_plot_units='mV')  # black
    g = gui.add_graph()
    g.add_ion_conc(comp, "cli", line_style='g')  # green
    g.add_ion_conc(comp, "ki", line_style='c')  # cyan
    g.add_ion_conc(comp, "nai", line_style='r')  # red
    g.add_ion_conc(comp, "xi", line_style='b')  # blue

    print("Ion concentrations")
    for ion in ["cli", "ki", "nai", "xi"]:
        print("{}.{}:{}".format(comp.name, ion, comp[ion]))

    comp2 = comp.copy("dendrite")

    # set diffusion value
    cli_D = 2.03  # um2/ms
    cli_D *=1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
    ki_D = 1.96  # um2/ms
    ki_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
    nai_D = 1.33
    nai_D *= 1e-5 ** 2
    
    # create diffusion connection
    diffusion_object = Diffusion(comp, comp2, ions={'cli': cli_D, 'ki': ki_D, 'nai':nai_D})

    v.add_voltage(comp2, line_style='--k', y_units_scale=1000, y_plot_units='mV')  # black
    g.add_ion_conc(comp2, "cli", line_style='--g')  # green
    g.add_ion_conc(comp2, "ki", line_style='--c')  # cyan
    g.add_ion_conc(comp2, "nai", line_style='--r')  # red
    g.add_ion_conc(comp2, "xi", line_style='--b')  # blue
    cli_graph = gui.add_graph() \
        .add_ion_conc(comp2, "cli", line_style='--g') \
        .add_ion_conc(comp, "cli", line_style='g')
    vol_graph = gui.add_graph() \
        .add_ion_conc(comp, "w", line_style='b') \
        .add_ion_conc(comp2, "w", line_style='b--')

    #update anion conductance
    
    comp2.gx=1e-9
    #comp2.an=True
    if comp2.an==True:
        z_graph = gui.add_graph() \
            .add_ion_conc(comp, "z",line_style='p-')\
            .add_ion_conc(comp2,"z",line_style='p--') #obviously, z is not an ion!
        
    sim.run(stop=100, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)
    print("Ion concentrations after anion flux from the dendritic compartment")
    for ion in ["cli", "ki", "nai", "xi"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))

    input("Press Enter to continue...")

    comp2.gx=0e-9

    #comp2.p=1e-4
    sim.run(stop=50, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=True)
    print("Ion concentrations after anion flux from the dendritic compartment is halted")
    for ion in ["cli", "ki", "nai", "xi"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))
    return()

anions()
