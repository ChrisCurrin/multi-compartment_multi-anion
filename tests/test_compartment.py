from unittest import TestCase
import simulator
from compartment import Compartment
from tests.slow_increase import slow_increase

class TestCompartment(TestCase):
    def setUp(self):
        try:
            self.sim = simulator.Simulator(False)
        except RuntimeError:
            self.sim = simulator.Simulator.get_instance()

        self.comp = Compartment("comp")

    def test_init(self):
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            comp = Compartment("init", pkcc2=0, z=-0.85,
                               cli=0.015292947537423218,
                               ki=0.023836660428807395,
                               nai=0.1135388427892471)
            self.assertEqual("Compartment {} not osmo-neutral\n".format(comp), f.getvalue())
        with self.assertRaises(Exception):
            comp = Compartment("init", pkcc2=0, z=-0.01, nai=50e-3, ki=80e-3)
        # with redirect_stdout(f):
        #     comp = Compartment("init", pkcc2=0, z=-0.01, nai=50e-3, ki=80e-3)
        #     self.assertNotEqual("Compartment {} not osmo-neutral\n".format(comp), f.getvalue())
        with self.assertRaises(ZeroDivisionError):
            Compartment("init", pkcc2=0, z=-0)
        with self.assertRaises(ZeroDivisionError):
            Compartment("init", pkcc2=0, z=-1)
        try:
            Compartment("init", pkcc2=0, z=-1, cli=1e-3)
        except ZeroDivisionError:
            self.fail("unexpected ZeroDivisionError error")

    def test_step(self):
        with self.assertRaises(ValueError):
            self.comp.step(None)
        prev_V = self.comp.V
        self.comp.step(self.sim.time())
        self.assertNotEqual(prev_V, self.comp.V)
        # check update list populated by step
        self.assertIsNot(self.sim._Simulator__update_list, [])

    def test_update_values(self):
        # compartment not at equilibrium in setUp, so changes occur 'naturally'
        prev_cli = self.comp.cli
        self.comp.update_values()
        self.assertNotEqual(prev_cli, self.comp.cli)

    def test_copy(self):

        copy = self.comp.copy(self.comp.name)
        # change only thing that should be different
        copy.unique_id = self.comp.unique_id
        self.assertEqual(self.comp.__dict__, copy.__dict__)

    def test_deepcopy(self):
        from copy import deepcopy
        import time
        # have the system sleep so copy is not created too close to original comp
        time.sleep(0.1)
        copy = self.comp.deepcopy(self.comp.name)
        self.assertNotEqual(self.comp.unique_id, copy.unique_id)
        # change only thing that should be different
        copy.unique_id = self.comp.unique_id
        self.assertEqual(self.comp.__dict__, copy.__dict__)
        self.assertEqual(deepcopy(self.comp).__dict__, self.comp.__dict__)

    def test_stable_state(self,ion='cli',gui=True):
        sim = self.sim
        comp = self.comp
        comp2 = self.comp.copy(self.comp.name)

        print("before run:\nion: \t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                          round(comp2[ion], 5)))
        print("\n  V: \t{}:{} \t {}:{}".format(comp.name, round(comp.V, 5), comp2.name, round(comp2.V, 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))
        sim.run(stop=200, plot_update_interval=50, dt=0.001)
        # value of V fixed
        print("after run:\nion: \t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                         round(comp2[ion], 5)))
        print("\n  V: \t{}:{} \t {}:{}".format(comp.name, round(comp.V, 5), comp2.name, round(comp2.V, 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))

        increase_amount = 1e-2
        comp.cli += increase_amount
        # comp.ki += increase_amount
        # slow_increase(1., increase_amount, comp, ["cli"],dt=0.001)
        if gui:
            g = sim.gui().add_graph()
            g.add_ion_conc(comp, ion, line_style='g')  # green
            v = sim.gui().add_graph()
            v.add_voltage(comp, line_style='k')
        print("value changed\nbefore run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name,
                                                                    round(comp2[ion], 5)))
        # self.assertNotEqual(round(comp[ion], 5), round(comp2[ion], 5))

            # g.ax.set_ylim([comp.cli,comp.cli+increase_amount])
            # v.ax.set_ylim([comp.V-0.02,comp.V+0.02])

        sim.run(continuefor=10, dt=0.001, block_after=False)

        sim.run(continuefor=0.001, dt=0.001, block_after=gui, print_time=False)
        print("after run:\n\t{}:{} \t {}:{}".format(comp.name, round(comp[ion], 5), comp2.name, round(comp2[ion], 5)))
        self.assertEqual(round(comp[ion], 5), round(comp2[ion], 5))
