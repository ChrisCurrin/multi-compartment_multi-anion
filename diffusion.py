import simulator
from compartment import Compartment
from sim_time import TimeMixin, Time


class Diffusion(TimeMixin):
    def __init__(self, comp_a: Compartment, comp_b: Compartment, ion: str, D: float):
        self.comp_a = comp_a
        self.comp_b = comp_b
        self.ion = ion
        self.D = D
        # register component with simulator
        simulator.Simulator.get_instance().register_compartment(self)

    def step(self, _time: Time = None):
        """
        Diffusion equation between compartments for each time step
        """
        F = self.ficks_law(self.ion, self.D)
        self.comp_a[self.ion] += F
        self.comp_b[self.ion] -= F

    def ficks_law(self, ion: str, D: float):
        """
        Fick's first law:
        F = -D * dc/dx
        F the rate of transfer per unit of a section
        c the concentration of diffusing substance
        x the space coordinate measured normal to the section
        :param ion: name of substance of interest
        :param D: diffusion constant
        :return:  F
        """
        # difference in ion concentrations
        dc = self.comp_a[ion] - self.comp_b[ion]
        # difference in distance between compartment midpoints
        dx = self.comp_a.L / 2 + self.comp_b.L / 2

        return -D * dc / dx

    def __getitem__(self, item):
        return self.__dict__[item]
