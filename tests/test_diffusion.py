import simulator
from diffusion import Diffusion
from compartment import Compartment
from unittest import TestCase
from common import default_length
from tests.slow_increase import slow_increase


class TestDiffusion(TestCase):
    def setUp(self):
        self.sim = simulator.Simulator.get_instance()
        self.comp = SimpleCompartment("c1", pkcc2=0, z=-0.85,
                                      cli=0.005175478364339566, ki=0.111358641523315191, nai=0.025519187764070129)
        self.comp2 = self.comp.copy("c2")
        # get a reasonable negative voltage (V=--0.06892)
        self.comp.cli += 2e-7
        self.comp2.cli += 2e-7
        self.ion = "cli"
        D = 1  # == 10-5 * cm2/s
        self.D = D * 1e-7  # um2 to dm2 (D in dm2/s)
        self.ions = {"cli": self.D}
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
        # value of V fixed
        print("after run:\nion: \t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                         round(comp2[ion], 5)))
        print("\n  V: \t{}:{} \t {}:{}".format(comp.name, round(comp.V, 5), comp2.name, round(comp2.V, 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))


        increase_amount = 1e-2
        # comp.cli += increase_amount
        # comp.ki += increase_amount
        slow_increase(1., increase_amount, comp, ["cli"],dt=0.0001)

        if gui or self.gui:
            g = sim.gui().add_graph()
            g.add_ion_conc(comp2, self.ion, line_style='--g')  # green
            g.add_ion_conc(comp, self.ion, line_style='g')  # green
            v = sim.gui().add_graph()
            v.add_voltage(comp2, line_style='--k')  # black
            v.add_voltage(comp, line_style='k')
            # g.ax.set_ylim([comp.cli,comp.cli+increase_amount])
            # v.ax.set_ylim([comp.V-0.02,comp.V+0.02])

        print("value changed\nbefore run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                                    round(comp2[ion], 5)))
        # self.assertNotEqual(round(comp[ion], 5), round(comp2[ion], 5))


        sim.run(continuefor=time_stop, dt=0.001, block_after=False)

        sim.run(continuefor=0.001, dt=0.001, block_after=block_after, print_time=False)
        print("after run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name, round(comp2[ion], 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))

    def test_diffusion_compartments(self, **kwargs):
        self.d = Diffusion(self.comp, self.comp2, self.ions)
        self.run_diffusion(300, False, **kwargs)

    def test_fick_diffusion_compartments(self, **kwargs):
        self.d = FickDiffusion(self.comp, self.comp2, self.ions)
        self.run_diffusion(200, False, **kwargs)

    def test_ohm_diffusion_compartments(self, **kwargs):
        """
        Test diffusion between compartments with only Ohm's law taken into account.
        """
        self.d = OhmDiffusion(self.comp, self.comp2, self.ions)
        self.run_diffusion(10, False, block_after=False, **kwargs)

    def test_ohm_diffusion_compartments_complex(self, **kwargs):
        """
        Test diffusion between compartments with only Ohm's law taken into account.
        A normal Compartment (as opposed to SimpleCompartment) is used calculate V accurately
        """
        self.comp = Compartment("c1", z=-0.85,
                                cli=0.005175478364339566, ki=0.111358641523315191,
                                nai=0.025519187764070129)  # corrected values
        self.comp2 = self.comp.copy("c2")
        self.d = OhmDiffusion(self.comp, self.comp2, self.ions)
        self.run_diffusion(100, False, block_after=False, **kwargs)

    def test_multi(self):
        self.setUp()
        self.test_diffusion_compartments()
        self.setUp()
        self.test_fick_diffusion_compartments()
        self.setUp()
        self.test_ohm_diffusion_compartments()

    def test_one_is_two(self):
        """
        Changing to the same values of all (2) compartments is the same as changing as if it were compartment
        """
        self.compBase = Compartment("c1", length=10e-5, pkcc2=0, z=-0.85,
                                    cli=0.015292947537423218,
                                    ki=0.023836660428807395,
                                    nai=0.1135388427892471)

        self.comp = Compartment("c1", length=5e-5, pkcc2=0, z=-0.85,
                                cli=0.015292947537423218,
                                ki=0.023836660428807395,
                                nai=0.1135388427892471)
        self.comp2 = self.comp.copy("c2")
        # set diffusion value
        cli_D = 2.03
        cli_D *= 1e-7  # um2 to dm2 (D in dm2/s)
        ki_D = 1.96
        ki_D *= 1e-7  # um2 to dm2 (D in dm2/s)
        nai_D = 1.33
        nai_D *= 1e-7
        # create diffusion connection
        diffusion_object = Diffusion(self.comp, self.comp2, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})

        self.assertEqual(self.compBase.cli, self.comp.cli)

        self.sim.run(stop=100, dt=0.001, block_after=False)

        self.assertEqual(self.compBase.cli, self.comp.cli)
        self.assertEqual(self.comp.cli, self.comp2.cli)

        self.compBase.gx = self.comp.gx = self.comp2.gx = 1e-8

        self.sim.run(continuefor=1, dt=1e-6, block_after=False)

        self.assertEqual(self.compBase.cli, self.comp.cli)
        self.assertEqual(self.comp.cli, self.comp2.cli)

    def test_middle(self):
        """
        Changing middle compartment, affects outer compartments by the same amount
        """
        # TODO: why does 'Compartment' fail the test (presumable an anion issue causing different steady-state cli)
        self.compBase = SimpleCompartment("c1", pkcc2=1e-8, z=-0.85)
        self.comp = self.compBase.copy("left")
        self.comp2 = self.comp.copy("right")

        # set diffusion value
        cli_D = 2.03
        cli_D *= 1e-7  # um2 to dm2 (D in dm2/ss)
        ki_D = 1.96
        ki_D *= 1e-7  # um2 to dm2 (D in dm2/s)
        nai_D = 1.33
        nai_D *= 1e-7
        # create diffusion connection
        diffusion_object = Diffusion(self.comp, self.comp2, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})
        diffusion_object = Diffusion(self.comp2, self.compBase, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})

        self.sim.run(stop=100, dt=0.001, block_after=False)

        self.compBase.gx = 1e-8
        self.sim.run(continuefor=1, dt=1e-6, block_after=False)
        self.assertEqual(self.comp.cli, self.comp2.cli)

        self.compBase.gx = 0e-8
        self.sim.run(continuefor=1, dt=1e-6, block_after=False)
        self.assertEqual(self.comp.cli, self.comp2.cli)

    def test_mols(self):
        self.compBase = SimpleCompartment("c1", pkcc2=1e-8, z=-0.85,
                                          cli=0.015292947537423218,
                                          ki=0.023836660428807395,
                                          nai=0.1135388427892471)

        self.comp = self.compBase.copy("left")
        self.comp2 = self.comp.copy("right")
        self.compSingle = SimpleCompartment("cs", pkcc2=1e-8, z=-0.85,
                                            cli=0.015292947537423218,
                                            ki=0.023836660428807395,
                                            nai=0.1135388427892471,
                                            length=3 * default_length)
        # set diffusion value
        cli_D = 2.03
        cli_D *= 1e-7  # um2 to dm2 (D in dm2/s)
        ki_D = 1.96
        ki_D *= 1e-7  # um2 to dm2 (D in dm2/s)
        nai_D = 1.33
        nai_D *= 1e-7
        # create diffusion connection
        diffusion_object = Diffusion(self.comp, self.compBase, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})
        diffusion_object = Diffusion(self.comp2, self.compBase, ions={'cli': cli_D, 'ki': ki_D, 'nai': nai_D})

        self.sim.run(stop=100, dt=0.001, block_after=False)

        self.compBase.gx = 1e-8
        self.compSingle.gx = 1e-8
        self.sim.run(continuefor=1, dt=1e-6, block_after=False)

        xmol_3 = self.compBase.mols(self.compBase.xi) + self.comp.mols(self.comp.xi) + self.comp2.mols(self.comp2.xi)
        xmol_single = self.compSingle.mols(self.compSingle.xi)
        self.assertAlmostEqual(xmol_3, xmol_single)

        cmol_3 = self.compBase.mols(self.compBase.cli) + self.comp.mols(self.comp.cli) + self.comp2.mols(self.comp2.cli)
        cmol_single = self.compSingle.mols(self.compSingle.cli)
        self.assertAlmostEqual(cmol_3, cmol_single)


class SimpleCompartment(Compartment):
    """
    Compartment without any changing ion concentrations over time.
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
