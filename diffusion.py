import simulator
from compartment import Compartment
from sim_time import TimeMixin, Time
from constants import k, q, valence
from common import T


class Diffusion(TimeMixin):
    def __init__(self, comp_a: Compartment, comp_b: Compartment, ions: list, D: float):
        self.comp_a = comp_a
        self.comp_b = comp_b
        self.ions = ions
        self.D = D
        self.dx = self.comp_a.L / 2 + self.comp_b.L / 2
        # register component with simulator
        simulator.Simulator.get_instance().register_compartment(self)

    def step(self, _time: Time = None):
        """
        Diffusion equation between compartments for each time step
        """
        for ion in self.ions:
            # F in M/ms * dm
            F = self.ficks_law(ion, self.D / _time.dt)
            # drift in M/ms dm
            drift_a = self.ohms_law(self.comp_a, ion, self.D / _time.dt)
            # negative to account for dV calculated from comp_a to comp_b only (and not comp_b to comp_a)
            drift_b = -1*self.ohms_law(self.comp_b, ion, self.D / _time.dt)
            d_drift = (drift_b + drift_a)
            j_net = (F + d_drift) * (_time.dt / self.dx)
            #j_net_a = (F + drift_a) * (_time.dt / self.dx)
            # -F as it is equal but opposite of F w.r.t. comp_a (drift_b has already had this applied above)
            #j_net_b = (-F + drift_b) * (_time.dt / self.dx)
            simulator.Simulator.get_instance().to_update(self.comp_a, ion, j_net, simulator.UpdateType.CHANGE)
            simulator.Simulator.get_instance().to_update(self.comp_b, ion, -j_net, simulator.UpdateType.CHANGE)
            # self.comp_a[ion] += j_net
            # self.comp_b[ion] -= j_net

    def ficks_law(self, ion: str, D: float):
        """
        Fick's law for diffusion:
        F = -D * dc/dx
        F is the diffusion flux - the rate of transfer per unit of a section (M/ms * dm)
        c the concentration of diffusing substance (M)
        x the space coordinate measured normal to the section (dm)
        D the diffusion coefficient (dm2/ms)
        :param ion: name of substance of interest
        :param D: diffusion coefficient (dm2/ms) -> called from context where D/dt
        :return:  F
        """
        # difference in ion concentrations
        dc = self.comp_a[ion] - self.comp_b[ion]
        # difference in distance between compartment midpoints
        self.dx = self.comp_a.L / 2 + self.comp_b.L / 2

        return -D * dc / self.dx

    def ohms_law(self, comp: Compartment, ion: str, D: float = None, mu: float = None):
        """
        Ohm's law for drift
        drift = -mu*z*[C]*dV/dx
        drift is the drift flux (M/ms dm)
        mu (u) is mobility (dm2/(V*ms))
        z is valence of the ion
        [C] is concentration of the ion
        V is electric potential (V)
        x the space coordinate measured normal to the section (dm)
        :param comp: compartment of interest for ion drift flux
        :param ion: name of substance of interest
        :param D: diffusion coefficient (dm2/ms) -> called from context where D/dt
        :param mu: mobility (dm2/(V*ms)) -> called from context where mu/dt
        :return: drift
        """
        if mu is None:
            if D is None:
                raise RuntimeError("must specify at least one of D or mu in ohms_law method")
            mu = self.D_to_mu(D, ion)
        self.dV = self.comp_a.V - self.comp_b.V
        self.dx = self.comp_a.L / 2 + self.comp_b.L / 2
        return -mu*valence(ion)*comp[ion]*(self.dV/self.dx)

    def D_to_mu(self, D: float, ion: str):
        """

        :param D: the diffusion coefficient (dm2/ms)
        :param ion:
        :return:
        """
        return D * q * abs(valence(ion)) / (k * T)

    def mu_to_D(self, mu: float, ion: str):
        """
        D = mu * k * T / (q*z)
        D is the diffusion coefficient (dm2/ms)
        mu is mobility
        k is Boltzman Constant
        T is temperature in Kelvin
        q is charge
        z is valence of ion
        :param mu:
        :param ion:
        :return: D
        """
        return mu * k*T/(q*valence(ion))

    def __getitem__(self, item):
        return self.__dict__[item]
