import simulator
from compartment import Compartment


def slow_increase(time: float, total_increase: float, comp: Compartment, ions: list, dt: float = 0.0001):
    sim = simulator.Simulator.get_instance()
    start = sim.time().time
    goal = start + time
    steps = int(round(time / dt))
    time_step_increase = total_increase / steps
    start_conc = comp[ions[0]]
    print("slowly increasing {} by {} over {} with a dt of {}, starting from {}"
          .format(ions, total_increase, time, dt, start))

    for i in range(steps):
        for ion in ions:
            # artificially increase concentration
            comp[ion] += time_step_increase
        # move 1 time step
        sim.run(continuefor=dt, dt=dt, plot_update_interval=10, block_after=False, print_time=False)
    print(sim.time().time)
