#methods for plotting and heatmaps
#17 Feb 2017

import matplotlib.pyplot as plt
import numpy as np
from sim_time import TimeMixin, Time
import simulator
from deferred_update import UpdateType

class Colormap(TimeMixin):

    def __init__(self, name, totalh, comp):
        self.name = name
        self.totalh = totalh
        self.comp = comp
        self.comp0w = comp[0].w
        simulator.Simulator.get_instance().register_colormap(self)

    def cmap(self, matrix=[1,2,3,4,5],rads=[1,2,3,4,5],totalhts=0,r=0,h=10,color='hot',name='default'):
        blank_row=[h]*100
        a=[blank_row]
        for j in range(len(rads)):
            rd=round(rads[j])
            extra=round((100-rd)/2)
            extra2=100-extra-rd
            for i in range(30):
                a.append(([h]*extra)+([matrix[j]*1000]*rd)+([h]*extra2))
            a.append(blank_row)
        print("Radii:",rads)
        plt.figure()
        plt.imshow(a, cmap=color, interpolation='nearest', vmin=r, vmax=h)
        plt.colorbar()
        plt.axis('off')
        if name != 'default':
            #plt.savefig(name)
            plt.title(name)
        plt.show()

    def heatmap(self,compl, comp, compr, sc, totalh, all=0, init_vals=None, title=['default','default','default']):
        sc=1e7
        hts = [int(compl.r * sc), int(comp.r * sc)]
        ecl = [round(compl.ecl, 5), round(comp.ecl, 5)]
        vm = [round(compl.V, 5), round(comp.V, 5)]
        for i in compr:
            hts.append(int(i.r * sc))
            ecl.append(round(i.ecl, 5))
            vm.append(round(i.V, 5))
        df = np.subtract(vm, ecl)
        if totalh == 0:
            totalh = sum(hts)
        if init_vals == None:
            init_vals = [df,ecl,vm]
        else:
            self.cmap(np.abs(np.subtract(df,init_vals[0])), hts, totalh, name=title[0])
            if all != 0:
                self.cmap(np.abs(np.subtract(init_vals[1],ecl)), hts, totalh, name=title[1])
                self.cmap(np.abs(np.subtract(init_vals[2],vm)), hts, totalh, name=title[2])
        return totalh, init_vals

    def smallheatmap(self,comp, sc, totalh, all=0, init_val=None,name='default'):
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
            self.cmap(zeroes, hts, totalh,name=name)
            if all != 0:
                self.cmap(np.abs(np.subtract(init_vals[1],ecl)), hts, totalh)
                self.cmap(np.abs(np.subtract(init_vals[2],vm)), hts, totalh)
        return totalh, init_vals

    def step(self, _time: Time = None):
        simulator.Simulator.get_instance().to_update(self, self.name, self.update_values, UpdateType.FUNCTION)

    def update_values(self):
        new_w = 0
        for i in range(len(self.comp)):
            new_w += self.comp[i].w
        self.totalh = new_w
        self.comp0w = self.comp[0].w

    def __getitem__(self, item):
        return getattr(self, item)