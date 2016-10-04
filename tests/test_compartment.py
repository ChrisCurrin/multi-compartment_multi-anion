from unittest import TestCase
import simulator
from compartment import Compartment


class TestCompartment(TestCase):
    def setUp(self):
        try:
            self.sim = simulator.Simulator(False)
        except RuntimeError:
            self.sim = simulator.Simulator.get_instance()

        self.comp = Compartment("comp", pkcc2=0, z=-0.85,
                                cli=0.015292947537423218,
                                ki=0.023836660428807395,
                                nai=0.1135388427892471)

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
        with self.assertRaises(RuntimeError):
            comp = Compartment("init", pkcc2=0, z=-0.85, nai=50e-3, ki=80e-3)
        with redirect_stdout(f):
            comp = Compartment("init", pkcc2=0, z=-0.01, nai=50e-3, ki=80e-3)
            self.assertNotEqual("Compartment {} not osmo-neutral\n".format(comp), f.getvalue())
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
        prev_L = self.comp.L
        self.comp.update_values()
        self.assertNotEqual(prev_L, self.comp.L)

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
