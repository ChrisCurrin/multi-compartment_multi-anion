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
    dt = 0.001*1e0  # s

    length = default_length_short

    if grow == 1:
        length = 5e-5
        dt = 0.001

    comp = Compartment("reference", z=-0.85
                       , cli=0.00433925284075134,
                       ki=0.1109567493822927,
                       nai=0.0255226350779378,
                       length=10e-5,
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
    sim.run(stop=50, dt=0.001, plot_update_interval=500, data_collect_interval=5, block_after=False)

    # set diffusion value
    cli_D *= 1e-7  # cm2 to dm2 (D in dm2/s)
    ki_D = 1.96
    ki_D *= 1e-7  # cm2 to dm2 (D in dm2/s)
    nai_D = 1.33
    nai_D *= 1e-7
    diffusion_object = []

    # connect with Diffusion
    diffusion_object.append(Diffusion(compl, comp, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D}))
    diffusion_object.append(Diffusion(comp, compr[-1], ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D}))
    for i in range(nrcomps):
        diffusion_object.append(Diffusion(compr[-2], compr[-1], ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D}))

    # heatmap incorporating compartment heights
    sc = 1e5
    if grow == 1:
        sc = 1e6
    hts = [int(compl.L * sc), int(comp.L * sc)]
    ecl = [round(compl.ecl, 5), round(comp.ecl, 5)]
    vm = [round(compl.V, 5), round(comp.V, 5)]
    for i in compr:
        hts.append(int(i.L * sc))
        ecl.append(round(i.ecl, 5))
        vm.append(round(i.V, 5))
    df = np.subtract(vm, ecl)
    totalh = sum(hts)
    cmap(ecl, hts, totalh)
    cmap(vm, hts, totalh, r=-100, h=-70, color='Greys')
    cmap(df, hts, totalh, r=10, h=-10, color='seismic')

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

    # run simulation with diffusion
    sim.run(continuefor=10, dt=dt, plot_update_interval=10, data_collect_interval=0.025)
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
            .add_ion_conc(comp, "absox", line_style='m')

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

    sim.run(continuefor=textra, dt=dt*0.001, plot_update_interval=textra, data_collect_interval=0.025)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations given event from the dendritic compartment")

    comp.gx = prev_comp_gx
    comp.jkccup = None

    if grow == 1:
        for a in compr:
            heatmap(compl, comp, compr, sc, totalh)
            a.gx = 1
            sim.run(continuefor=textra, dt=dt*0.001, plot_update_interval=textra, data_collect_interval=0.025)
            a.gx = 0

    sim.run(continuefor=textra*20, dt=dt*0.001, plot_update_interval=textra, data_collect_interval=0.025)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations at end")

    # heatmap incorporating compartment heights
    heatmap(compl, comp, compr, sc, totalh, all=1)

    return sim, gui


def main_old(cli_D=2.03, new_gx=1e-8, anion_flux=True, default_xz=-0.85, jkccup=None):
    """
    cli_D  # dm2/s
    :return: sim, gui: it is useful to return these objects for access after simulation
    """
    print("main")
    sim = Simulator().get_instance()
    gui = sim.gui()
    dt = 0.001

    comp = Compartment("soma", z=-0.85
                       , cli=0.01819925284075134,
                       ki=0.019909567493822927,
                       nai=0.11094226350779378)

    comp = Compartment("soma", z=-0.85
                       , cli=0.00433925284075134,
                       ki=0.1109567493822927,
                       nai=0.0255226350779378)

    # find steady-state values of ions
    sim.run(stop=50, dt=0.001, plot_update_interval=500, data_collect_interval=5, block_after=False)

    # create copies on either side
    comp2 = comp.copy("dendrite")
    comp3 = comp.copy("dendrite 2")

    # set diffusion value
    cli_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/s)
    ki_D = 1.96
    ki_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/s)
    nai_D = 1.33
    nai_D *= 1e-5 ** 2

    # create connections between compartments with Diffusion
    diffusion_object = Diffusion(comp, comp2, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})
    diffusion_object2 = Diffusion(comp, comp3, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})

    # create plots
    # plot voltage and reversals
    voltage_reversal_graph = gui.add_graph() \
        .add_ion_conc(comp2, "ecl", line_style='--g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(comp3, "ecl", line_style=':g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(comp, "ecl", line_style='g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(comp2, "ek", line_style='--b', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(comp3, "ek", line_style=':b', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(comp, "ek", line_style='b', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(comp2, line_style='--k', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(comp3, line_style=':k', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(comp, line_style='k', y_units_scale=1000, y_plot_units='mV')

    # plot volumes
    vol_graph = gui.add_graph() \
        .add_ion_conc(comp, "w", line_style='b') \
        .add_ion_conc(comp3, "w", line_style=':b') \
        .add_ion_conc(comp2, "w", line_style='b--')

    # plot fluxes across membrane and between compartments
    # for cli
    cli_graph = gui.add_graph() \
        .add_ion_conc(diffusion_object, {"ionjnet": "cli"}, line_style='g') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "cli"}, line_style='--g') \
        .add_ion_conc(comp2, "dcli", line_style='--g') \
        .add_ion_conc(comp3, "dcli", line_style=':g') \
        .add_ion_conc(comp, "dcli", line_style='g')
    # for xi
    xi_graph = gui.add_graph() \
        .add_ion_conc(diffusion_object, {"ionjnet": "xi"}, line_style='g') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "xi"}, line_style='--g') \
        .add_ion_conc(comp2, "dxi", line_style='--c') \
        .add_ion_conc(comp3, "dxi", line_style=':c') \
        .add_ion_conc(comp, "dxi", line_style='c')
    # for ki
    ki_graph = gui.add_graph() \
        .add_ion_conc(diffusion_object, {"ionjnet": "ki"}, line_style='g') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "ki"}, line_style='--g') \
        .add_ion_conc(comp2, "dki", line_style='--b') \
        .add_ion_conc(comp3, "dki", line_style=':b') \
        .add_ion_conc(comp, "dki", line_style='b')
    # for nai
    nai_graph = gui.add_graph() \
        .add_ion_conc(diffusion_object, {"ionjnet": "nai"}, line_style='g') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "nai"}, line_style='--g') \
        .add_ion_conc(comp2, "dnai", line_style='--r') \
        .add_ion_conc(comp3, "dnai", line_style=':r') \
        .add_ion_conc(comp, "dnai", line_style='r')
    # all ions
    j_graph = gui.add_graph() \
        .add_ion_conc(diffusion_object, {"ionjnet": "cli"}, line_style='g') \
        .add_ion_conc(diffusion_object, {"ionjnet": "ki"}, line_style='b') \
        .add_ion_conc(diffusion_object, {"ionjnet": "nai"}, line_style='r') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "cli"}, line_style='--g') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "ki"}, line_style='--b') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "nai"}, line_style='--r') \
        .add_ion_conc(comp2, "dcli", line_style='--g') \
        .add_ion_conc(comp3, "dcli", line_style=':g') \
        .add_ion_conc(comp, "dcli", line_style='g') \
        .add_ion_conc(comp2, "dxi", line_style='--c') \
        .add_ion_conc(comp3, "dxi", line_style=':c') \
        .add_ion_conc(comp, "dxi", line_style='c') \
        .add_ion_conc(comp2, "dnai", line_style='--r') \
        .add_ion_conc(comp3, "dnai", line_style=':r') \
        .add_ion_conc(comp, "dnai", line_style='r') \
        .add_ion_conc(comp2, "dki", line_style='--b') \
        .add_ion_conc(comp3, "dki", line_style=':b') \
        .add_ion_conc(comp, "dki", line_style='b')

    # run simulation with diffusion
    sim.run(continuefor=20, dt=dt, plot_update_interval=50, data_collect_interval=0.025)
    print_concentrations([comp, comp2, comp3],
                         title="Ion concentrations given diffusion between compartments")

    # (optionally) change anion conductance
    prev_comp2_gx = comp2.gx
    comp2.gx = new_gx
    if comp2.gx > 0:
        x_graph = gui.add_graph() \
            .add_ion_conc(comp, "absox", line_style='m') \
            .add_ion_conc(comp3, "absox", line_style='m:') \
            .add_ion_conc(comp2, "absox", line_style='m--')  # obviously, z is not an ion!

    # (optionally) change anion flux
    if anion_flux:
        comp2.xz = default_xz
        comp2.xmz = (comp2.z * comp2.xi - comp2.xz * comp2.xi_temp) / comp2.xm
        print('Anion flux with fixed anions having net charge', comp2.xmz, 'while a proportion of', (1 - comp2.ratio),
              'of all impermeants are temporarily mobile anions of charge', comp2.xz)
        z_graph = gui.add_graph() \
            .add_ion_conc(comp, "z", line_style='m') \
            .add_ion_conc(comp3, "z", line_style='m:') \
            .add_ion_conc(comp2, "z", line_style='m--')  # obviously, z is not an ion!

    # (optionally) change kcc2
    prev_comp2_pkcc2 = comp2.pkcc2
    if jkccup is not None:
        comp2.jkccup = jkccup
        g_graph = gui.add_graph() \
            .add_ion_conc(comp, "pkcc2", line_style='k') \
            .add_ion_conc(comp3, "pkcc2", line_style='k:') \
            .add_ion_conc(comp2, "pkcc2", line_style='k--')

    sim.run(continuefor=50, dt=dt, plot_update_interval=50, data_collect_interval=0.025)
    print_concentrations([comp, comp2, comp3],
                         title="Ion concentrations given anion flux from the dendritic compartment")

    comp2.gx = prev_comp2_gx
    comp2.jkccup = None
    comp2.pkcc2 = prev_comp2_pkcc2

    sim.run(continuefor=100, dt=dt, plot_update_interval=50, data_collect_interval=0.025)
    print_concentrations([comp, comp2, comp3],
                         title="Ion concentrations after anion flux from the dendritic compartment is halted")

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


def anions():
    """

    :return: sim, gui: it is useful to return these objects for access after simulation
    """
    print("main_anions")
    sim = Simulator().get_instance()
    gui = sim.gui()
    dt = 0.001
    # comp = Compartment("soma", pkcc2=0, z=-0.85)
    comp = Compartment("soma", z=-0.85  # )
                       , cli=0.01819925284075134,
                       ki=0.019909567493822927,
                       nai=0.11094226350779378)
    # v = gui.add_graph()
    # v.add_voltage(comp, line_style='k', y_units_scale=1000, y_plot_units='mV')  # black
    # g = gui.add_graph()
    # g.add_ion_conc(comp, "cli", line_style='g')  # green
    # g.add_ion_conc(comp, "ki", line_style='c')  # cyan
    # g.add_ion_conc(comp, "nai", line_style='r')  # red
    # g.add_ion_conc(comp, "xi", line_style='b')  # blue
    # find steady-state values of ions
    sim.run(stop=25, dt=0.001, plot_update_interval=500, data_collect_interval=5, block_after=False)
    # soma.cli:0.01819948776551597
    # soma.ki:0.019909327159644736
    # soma.nai:0.11094252293794836
    # soma.xi:0.13254866213689095

    comp2 = comp.copy("dendrite")
    comp3 = comp.copy("dendrite 2")

    # set diffusion value
    cli_D = 2.03
    cli_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/s)
    ki_D = 1.96
    ki_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/s)
    nai_D = 1.33
    nai_D *= 1e-5 ** 2

    # create diffusion connection
    diffusion_object = Diffusion(comp, comp2, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})
    diffusion_object2 = Diffusion(comp, comp3, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})

    # v.add_voltage(comp2, line_style='--k', y_units_scale=1000, y_plot_units='mV')  # black
    # g.add_ion_conc(comp2, "cli", line_style='--g')  # green
    # g.add_ion_conc(comp2, "ki", line_style='--c')  # cyan
    # g.add_ion_conc(comp2, "nai", line_style='--r')  # red
    # g.add_ion_conc(comp2, "xi", line_style='--b')  # blue
    cli_graph = gui.add_graph() \
        .add_ion_conc(comp2, "ecl", line_style='--g') \
        .add_ion_conc(comp3, "ecl", line_style=':g') \
        .add_ion_conc(comp, "ecl", line_style='g') \
        .add_ion_conc(comp2, "ek", line_style='--b') \
        .add_ion_conc(comp3, "ek", line_style=':b') \
        .add_ion_conc(comp, "ek", line_style='b') \
        .add_voltage(comp2, line_style='--k') \
        .add_voltage(comp3, line_style=':k') \
        .add_voltage(comp, line_style='k')
    vol_graph = gui.add_graph() \
        .add_ion_conc(comp, "w", line_style='b') \
        .add_ion_conc(comp3, "w", line_style=':b') \
        .add_ion_conc(comp2, "w", line_style='b--')
    j_graph = gui.add_graph() \
        .add_ion_conc(diffusion_object, {"ionjnet": "cli"}, line_style='g') \
        .add_ion_conc(diffusion_object, {"ionjnet": "ki"}, line_style='b') \
        .add_ion_conc(diffusion_object, {"ionjnet": "nai"}, line_style='r') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "cli"}, line_style='--g') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "ki"}, line_style='--b') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "nai"}, line_style='--r') \
        .add_ion_conc(comp2, "dcli", line_style='--k') \
        .add_ion_conc(comp3, "dcli", line_style=':k') \
        .add_ion_conc(comp, "dcli", line_style='k') \
        .add_ion_conc(comp2, "dxi", line_style='--c') \
        .add_ion_conc(comp3, "dxi", line_style=':c') \
        .add_ion_conc(comp, "dxi", line_style='c')

    dcli_graph = gui.add_graph() \
        .add_ion_conc(comp2, "dcli", line_style='--k') \
        .add_ion_conc(comp3, "dcli", line_style=':k') \
        .add_ion_conc(comp, "dcli", line_style='k') \
        .add_ion_conc(comp2, "dxi", line_style='--g') \
        .add_ion_conc(comp3, "dxi", line_style=':g') \
        .add_ion_conc(comp, "dxi", line_style='g')
    sim.run(continuefor=20, dt=dt, plot_update_interval=50, data_collect_interval=0.025)
    print("Ion concentrations given diffusion between compartments")
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))

    # update anion conductance

    comp2.gx = 1e-8
    if comp2.gx > 0:
        x_graph = gui.add_graph() \
            .add_ion_conc(comp, "absox", line_style='m') \
            .add_ion_conc(comp3, "absox", line_style='m:') \
            .add_ion_conc(comp2, "absox", line_style='m--')  # obviously, z is not an ion!

    comp2.an = True
    if comp2.an:
        comp2.ratio = 0.98  # ratio of fixed anions
        z_graph = gui.add_graph() \
            .add_ion_conc(comp, "z", line_style='m') \
            .add_ion_conc(comp3, "z", line_style='m:') \
            .add_ion_conc(comp2, "z", line_style='m--')  # obviously, z is not an ion!

    comp2.jkccup = False
    # comp2.pkcc2 = 10e-8
    if comp2.jkccup:
        g_graph = gui.add_graph() \
            .add_ion_conc(comp, "pkcc2", line_style='k') \
            .add_ion_conc(comp3, "pkcc2", line_style='k:') \
            .add_ion_conc(comp2, "pkcc2", line_style='k--')

    sim.run(continuefor=25, dt=dt, plot_update_interval=50, data_collect_interval=0.025)
    print("Ion concentrations given anion flux from the dendritic compartment")
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))

    sim.run(continuefor=26, dt=dt, plot_update_interval=50, data_collect_interval=0.025)
    print("Ion concentrations given anion flux from the dendritic compartment")
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))

    comp2.gx = 0e-9
    comp2.jkccup = False
    comp2.pkcc2 = 1e-8

    # comp2.p=1e-4
    sim.run(continuefor=100, dt=dt, plot_update_interval=50, data_collect_interval=0.025)
    print("Ion concentrations after anion flux from the dendritic compartment is halted")
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion], comp3.name, ion,
                                             comp[ion]))

    sim.run(continuefor=2, dt=dt, plot_update_interval=50, data_collect_interval=0.025)
    return sim, gui


def single():
    """

        :return: sim, gui: it is useful to return these objects for access after simulation
    """
    print("single compartment")
    sim = Simulator().get_instance()
    gui = sim.gui()
    dt = 0.001

    comp = Compartment("soma", z=-0.85, cli=4.34333e-3, ki=0, nai=25.562e-3)
    # find steady state
    sim.run(continuefor=50, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)

    g = gui.add_graph() \
        .add_ion_conc(comp, "ecl", line_style='g') \
        .add_ion_conc(comp, "ek", line_style='b') \
        .add_voltage(comp, line_style='k')

    w = gui.add_graph() \
        .add_ion_conc(comp, "w", line_style='k')

    sim.run(continuefor=10, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)

    comp.gx = 1e-8
    sim.run(continuefor=50, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)
    comp.gx = 0e-8
    sim.run(continuefor=25, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)
    return sim, gui


def heatmap(compl, comp, compr, sc, totalh, all=0):
    hts = [int(compl.L * sc), int(comp.L * sc)]
    ecl = [round(compl.ecl, 5), round(comp.ecl, 5)]
    vm = [round(compl.V, 5), round(comp.V, 5)]
    for i in compr:
        hts.append(int(i.L * sc))
        ecl.append(round(i.ecl, 5))
        vm.append(round(i.V, 5))
    df = np.subtract(vm, ecl)
    cmap(df, hts, totalh, r=-10, h=10, color='seismic')
    if all != 0:
        cmap(ecl, hts, totalh)
        cmap(vm, hts, totalh, -100, h=-70, color='Greys')
    return


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
    [sim, gui] = main(new_gx=1, jkccup=0e-25, anion_flux=False, default_xz=-1, nrcomps=7, dz=0, textra=10, grow=0)

    #sim.dispose()
    #print(args)
    #[sim, gui] = main(new_gx=1, jkccup=0e-25, anion_flux=True, default_xz=-1, nrcomps=7, dz=0, textra=10, grow=0)

    #sim.dispose()
    #print(args)
    #[sim, gui] = main(new_gx=0, jkccup=1e-12, anion_flux=False, default_xz=-1, nrcomps=7, dz=0, textra=10, grow=0)

    # [sim, gui] = main_old()

    if dispose_after:
        sim.dispose()
    else:
        # run a short sim with the intention of blocking if there is an arg
        sim.run(continuefor=0.001, dt=0.001, block_after=block_after)
