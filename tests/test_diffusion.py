import simulator
from diffusion import Diffusion
from compartment import Compartment
from unittest import TestCase


class TestDiffusion(TestCase):
    def setUp(self):
        self.sim = simulator.Simulator(False)
        self.comp = SimpleCompartment("c1", pkcc2=0, z=-0.85,
                                      cli=0.015292947537423218,
                                      ki=0.023836660428807395,
                                      nai=0.1135388427892471)
        self.comp2 = self.comp.copy("c2")
        # get a reasonable negative voltage (V=--0.05271)
        self.comp.cli += 2e-5
        self.comp2.cli += 2e-5
        self.ion = "cli"
        D = 1  # um2/ms # == 10-5 * cm2/s
        self.D = D * 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
        self.ions = {"cli": D}
        self.gui = False

    def run_diffusion(self, time_stop=10, gui=False, block_after=False):
        """
        Helper method for unit tests
        """
        sim = self.sim
        comp = self.comp
        comp2 = self.comp2
        ion = self.ion
        print("before run:\nion: \t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                          round(comp2[ion], 5)))
        print("\n  V: \t{}:{} \t {}:{}".format(comp.name, round(comp.V, 5), comp2.name, round(comp2.V, 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))
        sim.run(stop=10, dt=0.001)
        print("after run:\nion: \t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                         round(comp2[ion], 5)))
        print("\n  V: \t{}:{} \t {}:{}".format(comp.name, round(comp.V, 5), comp2.name, round(comp2.V, 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))
        comp.cli += 1e-3
        # comp.ki += 1e-3
        print("value changed\nbefore run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                                    round(comp2[ion], 5)))
        self.assertNotEqual(round(comp[ion], 5), round(comp2[ion], 5))
        if gui or self.gui:
            g = sim.gui().add_graph()
            g.add_ion_conc(comp2, "cli", line_style='--g')  # green
            g.add_ion_conc(comp, "cli", line_style='g')  # green
            v = sim.gui().add_graph()
            v.add_voltage(comp2, line_style='--k', units_scale=1000, plot_units='mV')  # black
            v.add_voltage(comp, line_style='k', units_scale=1000, plot_units='mV')

        sim.run(stop=time_stop, dt=0.001, block_after=block_after)
        print("after run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name, round(comp2[ion], 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))

    def test_diffusion_compartments(self):
        self.d = Diffusion(self.comp, self.comp2, self.ions)
        self.run_diffusion(50, True, True)

    def test_fick_diffusion_compartments(self):
        self.d = FickDiffusion(self.comp, self.comp2, self.ions)
        self.run_diffusion(50, True, True)

    def test_ohm_diffusion_compartments(self):
        """
        Test diffusion between compartments with only Ohm's law taken into account.
        :return:
        """
        self.d = OhmDiffusion(self.comp, self.comp2, self.ions)
        self.run_diffusion(50, True, True)

    def test_ohm_diffusion_compartments_complex(self):
        """
        Test diffusion between compartments with only Ohm's law taken into account.
        A normal Compartment (as opposed to SimpleCompartment) is used calculate V accurately
        :return:
        """
        self.comp = Compartment("c1", pkcc2=0, z=-0.85,
                                cli=0.015292947537423218, ki=0.023836660428807395, nai=0.1135388427892471)
        self.comp2 = self.comp.copy("c2")
        self.d = OhmDiffusion(self.comp, self.comp2, self.ions)
        self.run_diffusion(1, True, True)

    def test_multi(self):
        self.setUp()
        self.test_diffusion_compartments()
        self.setUp()
        self.test_fick_diffusion_compartments()
        self.setUp()
        self.test_ohm_diffusion_compartments()

    def test_step(self):
        # self.fail()
        pass

    def test_ficks_law(self):
        # self.fail()
        pass

    def test_one_is_two(self):
        self.compBase = Compartment("c1", length=100, pkcc2=0, z=-0.85,
                                cli=0.015292947537423218,
                                ki=0.023836660428807395,
                                nai=0.1135388427892471)

        self.comp = Compartment("c1", length=50, pkcc2=0, z=-0.85,
                                    cli=0.015292947537423218,
                                    ki=0.023836660428807395,
                                    nai=0.1135388427892471)
        self.comp2 = self.comp.copy("c2")
        # set diffusion value
        cli_D = 2.03  # um2/ms
        cli_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
        ki_D = 1.96  # um2/ms
        ki_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
        nai_D = 1.33
        nai_D *= 1e-5 ** 2
        # create diffusion connection
        diffusion_object = Diffusion(self.comp, self.comp2, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})

        self.assertEqual(self.compBase.cli, self.comp.cli)

        self.sim.run(stop=100, dt=0.001, block_after=False)

        self.assertEqual(self.compBase.cli, self.comp.cli)
        self.assertEqual(self.comp.cli, self.comp2.cli)

        self.compBase.gx = self.comp.gx = self.comp2.gx = 1e-8

        self.sim.run(continuefor=100, dt=0.001, block_after=False)

        self.assertEqual(self.compBase.cli, self.comp.cli)
        self.assertEqual(self.comp.cli, self.comp2.cli)

    def test_middle(self):
        self.compBase = Compartment("c1", length=100, pkcc2=1e-8, z=-0.85,
                                    cli=0.015292947537423218,
                                    ki=0.023836660428807395,
                                    nai=0.1135388427892471)

        self.comp = self.compBase.copy("left")
        self.comp2 = self.comp.copy("right")
        # set diffusion value
        cli_D = 2.03  # um2/ms
        cli_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
        ki_D = 1.96  # um2/ms
        ki_D *= 1e-5 ** 2  # um2 to dm2 (D in dm2/ms)
        nai_D = 1.33
        nai_D *= 1e-5 ** 2
        # create diffusion connection
        diffusion_object = Diffusion(self.comp, self.compBase, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})
        diffusion_object = Diffusion(self.comp2, self.compBase, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})

        self.sim.run(stop=100, dt=0.001, block_after=False)

        self.compBase.gx = 1e-8
        self.sim.run(continuefor=20, dt=0.001, block_after=False)
        self.assertEqual(self.comp.cli, self.comp2.cli)

        self.compBase.gx = 0e-8
        self.sim.run(continuefor=20, dt=0.001, block_after=False)
        self.assertEqual(self.comp.cli, self.comp2.cli)

class SimpleCompartment(Compartment):
    """
    Compartment without internally changing ion concentrations over time.
    Ion changes should only be done by a Diffusion class
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def copy(self, name):
        comp = SimpleCompartment(name, radius=self.r, length=self.L, pkcc2=self.pkcc2, z=self.z, nai=self.nai,
                                 ki=self.ki, cli=self.cli, p=self.p)
        return comp

    def step(self, _time=None):
        """
        Overriden method from Compartment to prevent internal ion changes
        Voltage updated for Ohm's law of drift considerations
        :param _time: Time object (required from abstract method)
        """
        self.V = self.FinvCAr * (self.nai + self.ki - self.cli + self.z * self.xi)
        # pass


class FickDiffusion(Diffusion):
    """
    Diffusion that only considers Fick's law of diffusion
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def ohms_law(self, comp: Compartment, ion: str, D: float = None, mu: float = None):
        return 0


class OhmDiffusion(Diffusion):
    """
    Diffusion that only considers Ohms's law of diffusion (aka drift)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def ficks_law(self, ion: str, D: float):
        return 0
