# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
from simulator import Simulator
from compartment import Compartment

def main():
    print("main")
    sim = Simulator()
    gui = sim.gui()
    comp = Compartment(kcc2=1)
    print(comp.cli)
    g = gui.new_graph()
    g.add_var(comp, "time", comp, "V")
    sim.run(stop=1000,plot_update_interval=100)
    print(comp.cli)
    g.update()

if __name__=="__main__":
    main()