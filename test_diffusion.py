import simulator
import copy
from diffusion import Diffusion
from compartment import Compartment
from unittest import TestCase


class TestDiffusion(TestCase):
    def test_diffusion_compartments(self):
        sim = simulator.Simulator(False)
        comp = SimpleCompartment("c1")
        comp2 = comp.copy("c2")
        ion = "cli"
        ions = ["cli"]
        D = 1  # um2/ms
        D = (D * 1e-5) ** 2  # um2 to dm2 (D in dm2/ms)
        d = Diffusion(comp, comp2, ions, D=D)
        print("before run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name, round(comp2[ion], 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))
        sim.run(stop=10, dt=0.001)
        print("after run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name, round(comp2[ion], 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))
        comp.cli += comp.cli / 2
        print("value changed\nbefore run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                                    round(comp2[ion], 5)))
        self.assertNotEqual(round(comp[ion], 5), round(comp2[ion], 5))
        g = sim.gui().add_graph()
        g.add_ion_conc(comp2, "cli", line_style='--g')  # green
        g.add_ion_conc(comp, "cli", line_style='g')  # green
        sim.run(stop=100, dt=0.001)
        print("after run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name, round(comp2[ion], 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))

    def test_step(self):
        # self.fail()
        pass

    def test_ficks_law(self):
        # self.fail()
        pass


class SimpleCompartment(Compartment):
    """
    Compartment without internally changing ion concentrations over time.
    Ion changes should only be done by a Diffusion class
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def copy(self, name):
        return copy.deepcopy(self)

    def step(self, _time=None):
        """
        Overriden method from Compartment to prevent internal ion changes
        :param _time: Time object (required from abstract method)
        """
        pass
