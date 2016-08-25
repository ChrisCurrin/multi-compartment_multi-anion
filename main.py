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
    comp = Compartment(kcc2=0,z=-0.85)
    print(comp.cli)
    g = gui.new_graph()
    g.add_var(comp, "time", comp, "V")      # black
    g2 = gui.new_graph()
    g2.add_var(comp, "time", comp, "cli")   # green
    g3 = gui.new_graph()
    g3.add_var(comp, "time", comp, "ki")    # cyan
    g4 = gui.new_graph()
    g4.add_var(comp, "time", comp, "nai")   # red
    g5 = gui.new_graph()
    g5.add_var(comp, "time", comp, "xi")    # dark blue
    time.clock()
    sim.run(stop=1000, plot_update_interval=1000)
    print(time.clock())
    print(comp.cli)
    g.update()

if __name__=="__main__":
    main()