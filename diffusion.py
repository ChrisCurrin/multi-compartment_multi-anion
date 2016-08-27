import simulator
from compartment import Compartment
from sim_time import TimeMixin, Time


class Diffusion(TimeMixin):
    def __init__(self, comp_a: Compartment, comp_b: Compartment, ion: str, D: float):
        self.comp_a = comp_a
        self.comp_b = comp_b
        self.ion = ion
        self.D = D
        self.dx = self.comp_a.L / 2 + self.comp_b.L / 2
        # register component with simulator
        simulator.Simulator.get_instance().register_compartment(self)

    def step(self, _time: Time = None):
        """
        Diffusion equation between compartments for each time step
        """
        F = self.ficks_law(self.ion, self.D/_time.dt)
        # F in M/ms * dm
        # should self.dx/2 be used instead?
        #   rationale for /2:
        #       the ions only need to travel half of dx to meet the other compartment's ions
        self.comp_a[self.ion] += F/_time.dt * self.dx
        self.comp_b[self.ion] -= F/_time.dt * self.dx

    def ficks_law(self, ion: str, D: float):
        """
        Fick's first law:
        F = -D * dc/dx
        F the rate of transfer per unit of a section (M/ms * dm)
        c the concentration of diffusing substance (M)
        x the space coordinate measured normal to the section (dm)
        D the diffusion constant (dm2/ms)
        :param ion: name of substance of interest
        :param D: diffusion constant (dm2/ms) -> called from context where D/dt
        :return:  F
        """
        # difference in ion concentrations
        dc = self.comp_a[ion] - self.comp_b[ion]
        # difference in distance between compartment midpoints
        self.dx = self.comp_a.L / 2 + self.comp_b.L / 2

        return -D * dc / self.dx

    def __getitem__(self, item):
        return self.__dict__[item]