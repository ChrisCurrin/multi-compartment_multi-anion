#methods for plotting and heatmaps
#17 Feb 2017

import matplotlib.pyplot as plt
import numpy as np

def cmap(matrix=[1,2,3,4,5],heights=[1,2,3,4,5]):
    a=[]
    for j in range(len(heights)):
        for i in range(heights[j]):
            a.append([matrix[j]*1000]*5)
        a.append([np.min(matrix)*1000-2]*5)
    print(a)
    plt.figure()
    plt.imshow(a, cmap='Blues', interpolation='nearest')
    plt.colorbar()
    plt.axis('off')
    plt.show()

if __name__=="__main__":
    cmap()