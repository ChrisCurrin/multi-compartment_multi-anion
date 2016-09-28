from unittest import TestCase
from simulator import Simulator
from compartment import Compartment
import time


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
        """
        RESULTS:
        run from 0 until 10 with time step of 0.001
        time taken for update interval of 0.01: 279.67880415916443
        time taken for update interval of 0.1: 22.88223671913147
        time taken for update interval of 1: 3.0911498069763184
        time taken for update interval of 2: 1.8190715312957764
        time taken for update interval of 5: 1.2316815853118896
        time taken for update interval of 10: 0.944373607635498
        time taken for update interval of 20: 0.9291894435882568
        """

        self.sim.dispose()
        self.sim = Simulator(_gui=True)
        comp = Compartment("soma")

        v = self.sim.gui().add_graph()
        v.add_voltage(comp, line_style='k')  # black
        stop = 5
        l = [0.1, 1, 2, 5, 10, 20]
        l.reverse()
        for pui in l:
            t_before = time.time()
            self.sim.run(stop=stop, plot_update_interval=pui, data_collect_interval=0.1, block_after=False)
            print("time taken for update interval of {}: {}".format(pui, time.time() - t_before))
        pass

    def test_register_compartment(self):
        comp = Compartment("comp")
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
