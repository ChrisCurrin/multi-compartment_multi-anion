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
from common import default_radius_short
from colormap import Colormap
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

def main(cli_D=2.03, new_gx=0e-8, anion_flux=False, default_xz=-0.85, jkccup=1e-12, nrcomps=2, dz=1e-7, textra=100, say='', stretch=False):
    """
    cli_D # um2/s
    :return: sim, gui: it is useful to return these objects for access after simulation
    """
    print("main")
    sim = Simulator().get_instance()
    gui = sim.gui()
    dt = 0.001  # s

    length = 10e-5

    comp = Compartment("reference", z=-0.85
                       , cli=0.0052,
                       ki=0.0123,
                       nai=0.014,
                       length=length,
                       radius=default_radius_short, stretch_w=stretch)

    # copies left
    compl = comp.copy("dendrite left")

    # copies right
    compr = []
    compr.append(comp.copy("dendrite right " + str(1)))
    for i in range(nrcomps):
        compr.append(comp.copy("dendrite right " + str(i + 2)))

    # find steady-state values of ions
    sim.run(stop=100, dt=0.001, plot_update_interval=50, data_collect_interval=5, block_after=False)

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
    sc = 1e7
    htplot = Colormap("cmap",0,compr)
    totalht, initvals = htplot.heatmap(compl, comp, compr, sc, 0, all=1, init_vals=None)
    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals)

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
    sim.run(continuefor=10, dt=dt, plot_update_interval=5, data_collect_interval=1)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations given diffusion between compartments")

    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals)

    # (optionally) change anion conductance
    prev_comp_gx = comp.gx
    comp.gx = new_gx
    comp.dz = dz

    voltage_reversal_graph_comp.save(say+'reference.eps')

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
        .add_ion_conc(compr[0], "w", line_style='b--')

    sim.run(continuefor=textra, dt=dt*0.001, plot_update_interval=textra/32, data_collect_interval=textra/32)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations during event from the dendritic compartment")
    # heatmap incorporating compartment heights
    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals, title=[say+'all_halfway_df.eps',say+'all_halfway_ecl.eps',say+'all_halfway_vm.eps'])

    voltage_reversal_graph_comp.save(say+'reference.eps')

    sim.run(continuefor=textra, dt=dt*0.001, plot_update_interval=textra/2, data_collect_interval=textra/16)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations immediately after event from the dendritic compartment")
    # heatmap incorporating compartment heights
    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals)

    comp.gx = prev_comp_gx
    comp.jkccup = 0
    comp.dz = 0

    voltage_reversal_graph_comp.save(say+'reference.eps')

    sim.run(continuefor=textra*1, dt=dt*0.001, plot_update_interval=textra/2, data_collect_interval=textra/4)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations at almost steady state")

    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals, title=[say+'all_end_df.eps',say+'all_end_ecl.eps',say+'all_end_vm.eps'])
    voltage_reversal_graph_comp.save(say+'reference.eps')

    sim.run(continuefor=textra*1, dt=dt*0.001, plot_update_interval=textra/2, data_collect_interval=textra/4)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations at steady state")

    # heatmap incorporating compartment heights
    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals, title=[say+'all_end_df.eps',say+'all_end_ecl.eps',say+'all_end_vm.eps'])
    voltage_reversal_graph_comp.save(say+'reference.eps')

    sim.run(continuefor=textra*2, dt=dt*0.001, plot_update_interval=textra/2, data_collect_interval=textra/4)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                     title="Ion concentrations at steady state")

    # heatmap incorporating compartment heights
    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals, title=[say+'all_end_df.eps',say+'all_end_ecl.eps',say+'all_end_vm.eps'])
    voltage_reversal_graph_comp.save(say+'reference.eps')

    sim.run(continuefor=textra*2, dt=dt*0.001, plot_update_interval=textra/2, data_collect_interval=textra/4)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations at steady state")

    # heatmap incorporating compartment heights
    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals, title=[say+'all_end_df.eps',say+'all_end_ecl.eps',say+'all_end_vm.eps'])
    voltage_reversal_graph_comp.save(say+'reference.eps')

    sim.run(continuefor=textra*2, dt=dt*0.001, plot_update_interval=textra/2, data_collect_interval=textra/4)
    print(datetime.datetime.now())
    print_concentrations([comp, compl, compr[-1]],
                         title="Ion concentrations at steady state")

    # heatmap incorporating compartment heights
    htplot.heatmap(compl, comp, compr, sc, totalht, all=1, init_vals=initvals, title=[say+'all_end_df.eps',say+'all_end_ecl.eps',say+'all_end_vm.eps'])
    voltage_reversal_graph_comp.save(say+'reference.eps')

    return sim, gui

def grow(nr=3, textra=10):
    print("growing via anions")
    sim = Simulator().get_instance()
    gui = sim.gui()
    dt = 0.001  # s

    comp = []
    comp.append(Compartment("initial growth cone", z=-0.85
                            , cli=0.00433925284075134,
                            ki=0.1109567493822927,
                            nai=0.0255226350779378,
                            length=5e-5,
                            radius=default_radius_short))

    # steady state
    sim.run(stop=100, dt=0.001, plot_update_interval=500, data_collect_interval=5, block_after=False)

    # set diffusion value
    cli_D = 2.03
    cli_D *= 1e-7  # cm2 to dm2 (D in dm2/s)
    ki_D = 1.96
    ki_D *= 1e-7  # cm2 to dm2 (D in dm2/s)
    nai_D = 1.33
    nai_D *= 1e-7

    #another compartment
    comp.append(comp[0].copy("compartment 1"))
    comp[1].L = 10e-5
    comp[1].w = np.pi * comp[1].r ** 2 * comp[1].L
    diffusion_object = [Diffusion(comp[0], comp[1], ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})]

    # heatmap incorporating compartment heights
    sc = 1e5
    htplot = Colormap("dendrite",comp[0].w+comp[1].w,comp)
    totalht, init_vals = htplot.smallheatmap(comp, sc, int(htplot.totalh*sc), all=0, init_val=None)

    # plot
    voltage_reversal_graph_comp = gui.add_graph() \
        .add_ion_conc(comp[0], "ecl", line_style='g', y_units_scale=1000, y_plot_units='mV') \
        .add_ion_conc(comp[0], "ek", line_style='b', y_units_scale=1000, y_plot_units='mV') \
        .add_voltage(comp[0], line_style='k', y_units_scale=1000, y_plot_units='mV')

    volume_graph = gui.add_graph()
    volume_graph.add_var(volume_graph.time,"time",htplot,"comp0w",line_style='k')
    volume_graph.add_var(volume_graph.time,"time",htplot,"totalh",line_style='b')

    sim.run(continuefor=1, dt=dt*0.001, plot_update_interval=0.5, data_collect_interval=textra/16)

    # growth
    for i in range(nr):
        htplot.smallheatmap(comp, sc, totalht, all=0, init_val=init_vals, name='graphs/grow_done'+str(i)+'.eps')
        comp[0].gx = 1

        # stop at certain length
        while comp[0].L < 15e-5:
            print("Fluxing compartment's length: "+str(comp[0].L))
            sim.run(continuefor=0.5, dt=dt*0.001, plot_update_interval=0.25, data_collect_interval=textra/16)
            if 9.9e-5<comp[0].L<10.3e-5:
                htplot.smallheatmap(comp, sc, totalht, all=0, init_val=init_vals, name='graphs/grow_interim'+str(i)+'.eps')
        comp[0].gx = 0
        print_concentrations(comp,str(i))

        # split compartments
        comp.insert(0,comp[0].copy("compartment "+str(i)))
        comp[1].L -= 5e-5
        comp[0].L = 5e-5
        comp[0].w = np.pi * comp[0].r ** 2 * comp[0].L
        comp[1].w = np.pi * comp[1].r ** 2 * comp[1].L

        print_concentrations(comp,str(i))

        # update total height
        htplot.comp = comp

        # update diffusion
        diffusion_object.append(Diffusion(comp[0], comp[1], ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D}))

        for a in comp:
            print(a.name)

        for j in diffusion_object:
            print(j.name)

        sim.run(continuefor=10, dt=dt*0.001, plot_update_interval=5, data_collect_interval=textra/16)

    htplot.smallheatmap(comp, sc, totalht, all=1, init_val=init_vals, name='graphs/grow_end.eps')
    sim.run(continuefor=4, dt=dt*0.001, plot_update_interval=2, data_collect_interval=0.5)
    htplot.smallheatmap(comp, sc, totalht, all=1, init_val=init_vals, name='graphs/grow_end.eps')

    return sim, gui

def print_concentrations(compartments, title=""):
    print(title)
    print("{:^10s}".format(''), end='\t')
    for comp in compartments:
        print("{:^20s}".format(comp.name), end='\t')
    print()
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w","ecl","V","z"]:
        print("{:10s}".format(ion), end='')
        for comp in compartments:
            print("{:^2.18f}".format(comp[ion]), end='\t')
        print()

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

    #[sim, gui] = main(new_gx=1, jkccup=None, anion_flux=False, default_xz=-1, nrcomps=7, dz=0, textra=15, say='graphs/g_rad_anionin_', stretch=False)

    [sim, gui] = main(new_gx=1, jkccup=0e-25, anion_flux=True, default_xz=-1, nrcomps=7, dz=0, textra=15, say='graphs/g_rad_dz_anionin_')

    #[sim, gui] = main(new_gx=0, jkccup=1e-14, anion_flux=False, default_xz=-1, nrcomps=7, dz=0, textra=15, say='graphs/f_rad_kcc_')

    #[sim, gui] = main(cli_D=0.203,new_gx=0, jkccup=1e-14, anion_flux=False, default_xz=-1, nrcomps=7, dz=0, textra=15, say='graphs/f_rad_dcli_')

    #[sim, gui] = grow(nr=3, textra=7)

    if dispose_after:
        sim.dispose()
    else:
        # run a short sim with the intention of blocking if there is an arg
        sim.run(continuefor=1e-6, dt=1e-6, block_after=block_after)
