from unittest import TestCase
from simulator import Simulator
from compartment import Compartment


class TestSimulator(TestCase):
    def setUp(self):
        self.sim = Simulator.get_instance()

    def test_gui(self):
        self.sim.dispose()
        self.sim = Simulator(_gui=True)
        self.assertIsNotNone(self.sim.gui())
        self.sim.dispose()
        self.sim = Simulator(_gui=False)
        self.assertIsNotNone(self.sim.gui())

    def test_get_instance(self):
        self.sim.dispose()
        self.sim = Simulator.get_instance()
        sim2 = Simulator.get_instance()
        self.assertIs(self.sim, sim2)
        with self.assertRaises(RuntimeError):
            self.sim = Simulator()

        self.sim.dispose()
        self.sim = Simulator()
        sim2 = Simulator.get_instance()
        self.assertIs(self.sim, sim2)
        with self.assertRaises(RuntimeError):
            self.sim = Simulator()

    def test_run(self):
        self.sim.run()
        pass

    def test_register_compartment(self):
        comp = Compartment()
        # Compartment auto-added to __object_list
        self.assertListEqual(self.sim.object_list(), [comp])
        # Dispose and create a new Simulator
        self.sim.dispose()
        self.sim = Simulator()
        self.sim.register_compartment(comp)
        self.assertListEqual(self.sim.object_list(), [comp])
        with self.assertRaises(TypeError):
            self.sim.register_compartment("Compartment")
        with self.assertRaises(TypeError):
            self.sim.register_compartment(True)
        with self.assertRaises(TypeError):
            self.sim.register_compartment(1)
        with self.assertRaises(TypeError):
            self.sim.register_compartment(0.1)

    def test_dipose(self):
        sim2 = Simulator.get_instance()
        self.assertIsNotNone(sim2.time())
        self.assertIs(self.sim.time(), sim2.time())
        self.sim.dispose()
        self.assertIsNone(sim2.time())
        self.assertIs(self.sim.time(), sim2.time())
