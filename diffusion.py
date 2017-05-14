import deferred_update
import simulator
from compartment import Compartment
from sim_time import TimeMixin, Time
from constants import k, q, valence
from common import T, RTF


class Diffusion(TimeMixin):
    def __init__(self, comp_a: Compartment, comp_b: Compartment, ions: dict):
        """
        Create a connection between compartments that allows for diffusion of ions.
        :param comp_a:
        :param comp_b:
        :param ions: dictionary must be of the form {ion: D}, where
                ion is the molecule of interest (str) (e.g. 'cli')
                D is the diffusion coefficient for that ion (float) (dm2/s)
        """
        self.name = comp_a.name + '<-' + comp_b.name
        print(self.name)
        self.comp_a = comp_a
        self.comp_b = comp_b
        self.ions = ions
        self.ionjnet = ions.copy()
        for ion, D in self.ions.items():
            # store D and mu for each ion
            self.ions[ion] = D
        # difference in distance between compartment midpoints
        self.dx = self.comp_a.L / 2 + self.comp_b.L / 2
        # register component with simulator
        simulator.Simulator.get_instance().register_compartment(self)

    def step(self, _time: Time = None):
        """
        Diffusion equation between compartments for each time step
        Fick's law calculates the diffusion due to concentration differences between compartments a and b
        Ohm's law calculates the diffusion due to ionic differences between compartments a and a
        Returned diffusion values are relative to comp_a
        """
        for ion, D in self.ions.items():
            # F in M * dm / s
            F = self.ficks_law(ion, D)
            # drift in M * dm / s
            d_drift = self.ohms_law(ion, D) * 1
            j_net = (F + d_drift / 2) * _time.dt
            simulator.Simulator.get_instance().to_update(self.comp_a, ion, j_net / self.comp_a.L,
                                                         deferred_update.UpdateType.CHANGE)
            # -j_net for comp_b as it is equal but opposite of j_net w.r.t. comp_a
            simulator.Simulator.get_instance().to_update(self.comp_b, ion, -j_net / self.comp_b.L,
                                                         deferred_update.UpdateType.CHANGE)
            self.ionjnet[ion] = j_net  # jnet has units M*dm

    def ficks_law(self, ion: str, D: float):
        """
        Fick's law for diffusion:
        F = -D * dc/dx
        F is the diffusion flux - the rate of transfer per unit of a section (M/s * dm)
        c the concentration of diffusing substance (M)
        x the space coordinate measured normal to the section (dm)
        D the diffusion coefficient (dm2/s)
        :param ion: name of substance of interest
        :param D: diffusion coefficient (dm2/s)
        :return:  F M*dm/s
        """
        # difference in ion concentrations
        dc = self.comp_a[ion] - self.comp_b[ion]
        # difference in distance between compartment midpoints
        self.dx = self.comp_a.L / 2 + self.comp_b.L / 2

        return -D * dc / self.dx

    def ohms_law(self, ion: str, D: float = None):
        """
        Ohm's law for drift
        drift = -D*z/RTF*dV/dx*[C]
        drift is the drift flux (M/s dm)
        D the diffusion coefficient (dm2/s)
        RTF is gas constant * temperature / Faraday's constant
        z is valence of the ion
        [C] is concentration of the ion
        V is electric potential (V)
        x the space coordinate measured normal to the section (dm)
        :param ion: name of substance of interest
        :param D: diffusion coefficient (dm2/s)
        :return: drift
        """
        dV = self.comp_a.V - self.comp_b.V
        # dx is calculated in init but must be recalculated as L changes with volume changes
        self.dx = self.comp_a.L / 2 + self.comp_b.L / 2

        return - (D / RTF * valence(ion) * dV / self.dx) * (self.comp_a[ion] + self.comp_b[ion])

    def __getitem__(self, item):
        return self.__dict__[item]