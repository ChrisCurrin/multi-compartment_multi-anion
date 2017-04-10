#methods for plotting and heatmaps
#17 Feb 2017

import matplotlib.pyplot as plt
import numpy as np

def cmap(matrix=[1,2,3,4,5],heights=[1,2,3,4,5],totalhts=0,r=-90,h=-85,color='Blues'):
    blank_row=[r]*5
    a=[blank_row]
    change=int(sum(heights)-totalhts)
    if change <0:
        for i in range(-change):
            a.append([r]*5)
    for j in range(len(heights)):
        for i in range(heights[j]):
            a.append([matrix[j]*1000]*5)
        a.append(blank_row)
    if change >0:
        for i in range(change):
            a.append(blank_row)
    plt.figure()
    plt.imshow(a, cmap=color, interpolation='nearest', vmin=r, vmax=h)
    plt.colorbar()
    plt.axis('off')
    plt.show()


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

def smallheatmap(comp, sc, totalh, all=0):
    hts = []
    ecl = []
    vm = []
    for i in comp:
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

if __name__=="__main__":
    cmap()