#methods for plotting and heatmaps
#17 Feb 2017

import matplotlib.pyplot as plt
import numpy as np

def cmap(matrix=[1,2,3,4,5],heights=[1,2,3,4,5],totalhts=0,r=-90,h=-85):
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
            a.append([r]*5)
    plt.figure()
    plt.imshow(a, cmap='Blues', interpolation='nearest', vmin=r, vmax=h)
    plt.colorbar()
    plt.axis('off')
    plt.show()

if __name__=="__main__":
    cmap()