# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwald
"""
import sys, getopt
from simulator import Simulator
from compartment import Compartment
from diffusion import Diffusion
from common import default_length_short, default_radius_short
from colormap import cmap
import numpy as np
import datetime

usage_help = \
    """
            main.py
    Usage:
    -h, --help              show this help menu
    -b, --block             block simulation
                            (control not returned to user)
    -c, --close             close all previous figures
    -d, --dispose           close all figures, including those produced during simulation
                            (control always returned to user; overrides --block)
"""


def main(cli_D=2.03, new_gx=0e-8, anion_flux=False, default_xz=-0.85, jkccup=1e-12, nrcomps=2, dz=1e-7, textra=100,
         grow=0):
    """
    cli_D # um2/s
    :return: sim, gui: it is useful to return these objects for access after simulation
    """
    print("main")
    sim = Simulator().get_instance()
    gui = sim.gui()
    dt = 0.001  # s

    length = 10e-5

    if grow == 1:
        length = 0.5e-5
        dt = 0.001

    comp = Compartment("reference", z=-0.85
                       , cli=0.00433925284075134,
                       ki=0.1109567493822927,
                       nai=0.0255226350779378,
                       length=length,
                       #length=length / (3.0 + nrcomps),
                       radius=default_radius_short)

    # copies left
    compl = comp.copy("dendrite left")

    # copies right
    compr = []
    compr.append(comp.copy("dendrite right " + str(1)))
    for i in range(nrcomps):
        compr.append(comp.copy("dendrite right " + str(i + 2)))

    # find steady-state values of ions
    sim.run(stop=100, dt=0.001, plot_update_interval=500, data_collect_interval=5, block_after=False)

    # set diffusion value
    cli_D *= 1e-7  # cm2 to dm2 (D in dm2/s)
    ki_D = 1.96
    ki_D *= 1e-7  # cm2 to dm2 (D in dm2/s)
    nai_D = 1.33
    nai_D *= 1e-7
    diffusion_object = []

    # connect with Diffusion
    diffusion_object.append(Diffusion(compl, comp, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D}))
    diffusion_object.append(Diffusion(comp, compr[0], ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D}))
    for i in range(nrcomps):
        diffusion_object.append(Diffusion(compr[i], compr[i+1], ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D}))

    # heatmap incorporating compartment heights
    sc = 1e5
    if grow == 1:
        sc = 1e6

    totalht = heatmap(compl, comp, compr, sc, 0, all=1)

    voltage_reversal_graph_comp = gui.add_graph() \
        .add_ion_conc(comp, "ecl", line_style='g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(comp, "ek", line_style='b', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(comp, line_style='k', y_units_scale=1000, y_plot_units='mV')

    voltage_reversal_graph_compr = gui.add_graph() \
        .add_ion_conc(compr[-1], "ecl", line_style='g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(compr[-1], "ek", line_style='b', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(compr[-1], line_style='k', y_units_scale=1000, y_plot_units='mV')

    voltage_reversal_graph_compl = gui.add_graph() \
        .add_ion_conc(compl, "ecl", line_style='g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(compl, "ek", line_style='b', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(compl, line_style='k', y_units_scale=1000, y_plot_units='mV')

    voltage_reversal_graph_compr1 = gui.add_graph() \
        .add_ion_conc(compr[0], "ecl", line_style='g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(compr[0], "ek", line_style='b', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(compr[0], line_style='k', y_units_scale=1000, y_plot_units='mV')

    voltage_reversal_graph_comprmid = gui.add_graph() \
        .add_ion_conc(compr[int(nrcomps/2)+1], "ecl", line_style='g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(compr[int(nrcomps/2)+1], "ek", line_style='b', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(compr[int(nrcomps/2)+1], line_style='k', y_units_scale=1000, y_plot_units='mV')

    # run simulation with diffusion
    sim.run(continuefor=10, dt=dt, plot_update_interval=50, data_collect_interval=10)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations given diffusion between compartments")

    # (optionally) change anion conductance
    prev_comp_gx = comp.gx
    comp.gx = new_gx
    comp.dz = dz

    if dz != 0:
        z_graph = gui.add_graph() \
            .add_ion_conc(comp, "z", line_style='m')

    if comp.gx > 0:
        x_graph = gui.add_graph() \
            .add_ion_conc(comp, "absox", line_style='m') \
            .add_ion_conc(compl, "absox", line_style=':m') \
            .add_ion_conc(compr[0], "absox", line_style='m--')

    # (optionally) change anion flux
    if anion_flux:
        comp.xz = default_xz
        comp.xmz = (comp.z * comp.xi - comp.xz * comp.xi_temp) / comp.xm
        print('Anion flux with fixed anions having net charge', comp.xmz, 'while a proportion of', (1 - comp.ratio),
              'of all impermeants are temporarily mobile anions of charge', comp.xz)

    z_graph = gui.add_graph() \
        .add_ion_conc(comp, "z", line_style='m')

    # (optionally) change kcc2
    prev_comp_pkcc2 = comp.pkcc2
    if jkccup is not None:
        comp.jkccup = jkccup
        g_graph = gui.add_graph() \
            .add_ion_conc(comp, "pkcc2", line_style='k')

    vol_graph = gui.add_graph() \
        .add_ion_conc(comp, "w", line_style='b') \
        .add_ion_conc(compl, "w", line_style=':b') \
        .add_ion_conc(compr[0], "w", line_style='b--')  # \
    # .add_ion_conc(compr[1], "w", line_style='b--') \
    # .add_ion_conc(compr[2], "w", line_style='b--')

    sim.run(continuefor=textra, dt=dt*0.001, plot_update_interval=textra/2, data_collect_interval=textra/16)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations given event from the dendritic compartment")

    comp.gx = prev_comp_gx
    comp.jkccup = 0
    comp.dz = 0

    if grow == 1:
        for a in compr:
            heatmap(compl, comp, compr, sc, totalht)
            a.gx = 1
            sim.run(continuefor=textra, dt=dt*0.0001, plot_update_interval=textra/2, data_collect_interval=textra/16)
            a.gx = 0

    sim.run(continuefor=textra*3, dt=dt*0.001, plot_update_interval=textra/2, data_collect_interval=textra/4)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations at end")

    # heatmap incorporating compartment heights
    heatmap(compl, comp, compr, sc, totalht, all=1)

    return sim, gui

def print_concentrations(compartments, title=""):
    print(title)
    print("{:^10s}".format(''), end='\t')
    for comp in compartments:
        print("{:^20s}".format(comp.name), end='\t')
    print()
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w"]:
        print("{:10s}".format(ion), end='')
        for comp in compartments:
            print("{:^2.18f}".format(comp[ion]), end='\t')
        print()

def heatmap(compl, comp, compr, sc, totalh, all=0):
    hts = [int(compl.L * sc), int(comp.L * sc)]
    ecl = [round(compl.ecl, 5), round(comp.ecl, 5)]
    vm = [round(compl.V, 5), round(comp.V, 5)]
    for i in compr:
        hts.append(int(i.L * sc))
        ecl.append(round(i.ecl, 5))
        vm.append(round(i.V, 5))
    df = np.subtract(vm, ecl)
    if totalh == 0:
        totalh = sum(hts)
    cmap(df, hts, totalh, r=0, h=10, color='PuRd')
    if all != 0:
        cmap(ecl, hts, totalh)
        cmap(vm, hts, totalh, -85, h=-80, color='Greys')
    return totalh


if __name__ == "__main__":
    argv = sys.argv[1:]  # (first arg is 'python')
    sim = Simulator.get_instance()
    gui = sim.gui()
    block_after = True
    dispose_after = False

    try:
        opts, args = getopt.getopt(argv, "hscd", ["help", "save", "close", "dispose"])
    except getopt.GetoptError:
        print(usage_help)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage_help)
            sys.exit()
        elif opt in ("-s", "--save"):
            block_after = False
        elif opt in ("-c", "--close"):
            print("closing...")
            gui.close_graphs()
        elif opt in ("-d", "--dispose"):
            dispose_after = True
    sim.dispose()
    print(args)
    #compartment dxi should be 1e-8
    #[sim, gui] = main(new_gx=1, jkccup=None, anion_flux=False, default_xz=-1, nrcomps=7, dz=0, textra=25, grow=0)

    #[sim, gui] = main(new_gx=0, jkccup=0e-25, anion_flux=False, default_xz=-1, nrcomps=7, dz=1e-7, textra=0, grow=0)

    [sim, gui] = main(new_gx=0, jkccup=1e-13, anion_flux=False, default_xz=-1, nrcomps=7, dz=0, textra=10, grow=0)

    #[sim, gui] = main(new_gx=0, jkccup=1e-12, anion_flux=False, default_xz=-1, nrcomps=3, dz=0, textra=0.001, grow=1)

    if dispose_after:
        sim.dispose()
    else:
        # run a short sim with the intention of blocking if there is an arg
        sim.run(continuefor=1e-6, dt=1e-6, block_after=block_after)
