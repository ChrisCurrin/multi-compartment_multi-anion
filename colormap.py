#methods for plotting and heatmaps
#17 Feb 2017

import matplotlib.pyplot as plt
import numpy as np
from sim_time import TimeMixin, Time

class Colormap(TimeMixin):

    def __init__(self, name, totalh, comp):
        self.name = name
        self.totalh = totalh
        self.comp = comp

    def cmap(self, matrix=[1,2,3,4,5],heights=[1,2,3,4,5],totalhts=0,r=0,h=5,color='hot'):
        blank_row=[h]*5
        a=[blank_row]
        change=int(sum(heights)-totalhts)
        if change <0:
            for i in range(-change):
                a.append([h]*5)
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

    def heatmap(self,compl, comp, compr, sc, totalh, all=0, init_vals=None):
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
        if init_vals == None:
            init_vals = [df,ecl,vm]
        else:
            self.cmap(np.abs(np.subtract(df,init_vals[0])), hts, totalh)
            if all != 0:
                self.cmap(np.abs(np.subtract(init_vals[1],ecl)), hts, totalh)
                self.cmap(np.abs(np.subtract(init_vals[2],vm)), hts, totalh)
        return totalh, init_vals

    def smallheatmap(self,comp, sc, totalh, all=0, init_val=None):
        print(init_val)
        hts = []
        ecl = []
        vm = []
        zeroes = []
        if init_val != None:
            init_vals = [[init_val[0][0]],[init_val[1][0]],[init_val[2][0]]]
        else:
            init_vals = init_val
        for i in comp:
            hts.append(int(i.L * sc))
            ecl.append(round(i.ecl, 5))
            vm.append(round(i.V, 5))
            if init_val != None:
                zeroes.append(0)
                for a in range(3):
                    init_vals[a].append(init_vals[a][0])
        print(init_vals)
        if init_val != None:
            init_vals[0].pop()
            init_vals[1].pop()
            init_vals[2].pop()
        df = np.subtract(vm, ecl)
        if totalh == 0:
            totalh = sum(hts)
        if init_val == None:
            init_vals = [[df[0]],[ecl[0]],[vm[0]]]
        else:
            self.cmap(np.abs(np.subtract(df,init_vals[0])), hts, totalh)
            self.cmap(zeroes, hts, totalh)
            if all != 0:
                self.cmap(np.abs(np.subtract(init_vals[1],ecl)), hts, totalh)
                self.cmap(np.abs(np.subtract(init_vals[2],vm)), hts, totalh)
        return totalh, init_vals

    def step(self, _time: Time = None):
        for i in range(len(self.comp)):
            self.totalh += self.comp[i].w

    def __getitem__(self, item):
        return self.__dict__[item]