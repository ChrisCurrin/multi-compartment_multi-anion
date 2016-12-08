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


def main():
    """

    :return: sim, gui: it is useful to return these objects for access after simulation
    """
    print("main")
    sim = Simulator().get_instance()
    gui = sim.gui()
    dt = 0.001
    # comp = Compartment("soma", pkcc2=0, z=-0.85)
    comp = Compartment("soma", pkcc2=0, z=-0.85  # )
                       , cli=0.01819925284075134,
                       ki=0.019909567493822927,
                       nai=0.11094226350779378)
    v = gui.add_graph()
    v.add_voltage(comp, line_style='k', y_units_scale=1000, y_plot_units='mV')  # black
    g = gui.add_graph()
    g.add_ion_conc(comp, "cli", line_style='g')  # green
    g.add_ion_conc(comp, "ki", line_style='c')  # cyan
    g.add_ion_conc(comp, "nai", line_style='r')  # red
    g.add_ion_conc(comp, "xi", line_style='b')  # blue
    # find steady-state values of ions
    sim.run(stop=50, dt=0.001, plot_update_interval=10, data_collect_interval=0.025, block_after=False)
    # values from steady-state
    # soma.cli:0.01819948776551597
    # soma.ki:0.019909327159644736
    # soma.nai:0.11094252293794836
    # soma.xi:0.13254866213689095

    print("Ion concentrations")
    for ion in ["cli", "ki", "nai", "xi"]:
        print("{}.{}:{}".format(comp.name, ion, comp[ion]))

    comp2 = comp.copy("dendrite")
    # change ion concentration
    comp2.cli -= 1e-3
    comp2.ki -= 1e-3

    # set diffusion value
    cli_D = 2.03  # um2/ms
    cli_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
    ki_D = 1.96  # um2/ms
    ki_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
    nai_D = 1.33
    nai_D *= 1e-5 ** 2
    # create diffusion connection
    diffusion_object = Diffusion(comp, comp2, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})

    print(diffusion_object.dx)
    print(diffusion_object.ficks_law("cli", D=cli_D) * dt / diffusion_object.dx)  # (M * dm) to (mM * um) per ms
    print("Ion concentrations")
    for ion in ["V", "cli", "ki", "nai", "xi"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))
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
    # sim.run(stop=0.1, dt=dt, plot_update_interval=dt, data_collect_interval=dt)
    sim.run(continuefor=50, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=True)
    print("Ion concentrations")
    for ion in ["cli", "ki", "nai", "xi"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))


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
    # values from steady-state
    # soma.cli:0.01819948776551597
    # soma.ki:0.019909327159644736
    # soma.nai:0.11094252293794836
    # soma.xi:0.13254866213689095

    comp2 = comp.copy("dendrite")
    comp3 = comp.copy("dendrite 2")

    # set diffusion value
    cli_D = 2.03  # um2/ms
    cli_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
    ki_D = 1.96  # um2/ms
    ki_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
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
        .add_ion_conc(diffusion_object, {"ionjnet": "cliplot"}, line_style='g') \
        .add_ion_conc(diffusion_object, {"ionjnet": "kiplot"}, line_style='b') \
        .add_ion_conc(diffusion_object, {"ionjnet": "naiplot"}, line_style='r') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "cliplot"}, line_style='--g') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "kiplot"}, line_style='--b') \
        .add_ion_conc(diffusion_object2, {"ionjnet": "naiplot"}, line_style='--r') \
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
    sim.run(continuefor=20, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)
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

    sim.run(continuefor=25, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)
    print("Ion concentrations given anion flux from the dendritic compartment")
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))

    sim.run(continuefor=26, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)
    print("Ion concentrations given anion flux from the dendritic compartment")
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion]))

    comp2.gx = 0e-9
    comp2.jkccup = False
    comp2.pkcc2 = 1e-8

    # comp2.p=1e-4
    sim.run(continuefor=100, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)
    print("Ion concentrations after anion flux from the dendritic compartment is halted")
    for ion in ["cli", "ki", "nai", "xi", "pkcc2", "gx", "w"]:
        print("{}.{}:{} \t {}.{}:{} ".format(comp.name, ion, comp[ion], comp2.name, ion, comp2[ion], comp3.name, ion,
                                             comp[ion]))

    sim.run(continuefor=2, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=False)
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
    sim.run(continuefor=25, dt=dt, plot_update_interval=50, data_collect_interval=0.025, block_after=True)
    return sim, gui

usage_help = """
            main.py
    Usage:
    -h, --help              show this help menu
    -b, --block             block simulation
                            (control not returned to user)
    -c, --close             close all previous figures
    -d, --dispose           close all figures, including those produced during simulation
                            (control always returned to user; overrides --block)
                """

if __name__ == "__main__":
    argv = sys.argv[1:]  # (first arg is 'python')
    sim = Simulator.get_instance()
    gui = sim.gui()
    block_after = False
    dispose_after = False

    try:
        opts, args = getopt.getopt(argv, "hbcd", ["help", "block", "close", "dispose"])
    except getopt.GetoptError:
        print(usage_help)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage_help)
            sys.exit()
        elif opt in ("-b", "--block"):
            block_after = True
        elif opt in ("-c", "--close"):
            print("closing...")
            gui.close_graphs()
        elif opt in ("-d", "--dispose"):
            dispose_after = True
    sim.dispose()
    print(args)
    [sim, gui] = anions()

    if dispose_after:
        sim.dispose()
    else:
        # run a short sim with the intention of blocking if there is an arg
        sim.run(continuefor=0.001, dt=0.001, block_after=block_after)