import math
import random
from models.coloring_state import Coloring
from models.graph import Graph


class SimulatedAnnealing:

    def __init__(
        self,
        graph: Graph,
        coloring_state: Coloring,
        max_iteration: int,
        initial_temp: float,
        cooling_rate: float
    ):
        self._graph = graph
        self._max_iteration = max_iteration
        self._initial_temp = initial_temp
        self._cooling_rate = cooling_rate

        self.current_state: Coloring = coloring_state
        self.best_state: Coloring = coloring_state.copy()
        self.temp: float = initial_temp
        self.iteration: int = 0


    def run(self) -> Coloring:
        while not self.step():
            pass
        return self.best_state


    def step(self) -> bool:

        if self.current_state.num_conflicts == 0:
            return True
        if self.iteration >= self._max_iteration or self.temp < 0.001:
            return True

        next_state = self._create_next_state(self.current_state)
        if next_state.num_conflicts == 0:
            self.current_state = next_state
            self.best_state = next_state.copy()
            return True

        conflict_delta = self.current_state.num_conflicts - next_state.num_conflicts
        if conflict_delta > 0:
            self.current_state = next_state
            if next_state.num_conflicts < self.best_state.num_conflicts:
                self.best_state = next_state.copy()
        else:
            if self._take_risk(conflict_delta, self.temp):
                self.current_state = next_state

        self.temp = self._calculate_temp(self.temp)
        self.iteration += 1

        return False


    def _create_next_state(self, coloring_state: Coloring) -> Coloring:
        state = coloring_state.copy()
        state.modify_one_vertex()
        return state

    def _take_risk(self, conflict_delta: int, temp: float) -> bool:
        if temp <= 0:
            return False

        probability = math.exp(conflict_delta / temp)
        return probability > random.random()

    def _calculate_temp(self, temp: float) -> float:
        return self._cooling_rate * temp



"""
def run(self) -> Coloring:
    current_state = self._coloring_state
    if current_state.num_conflicts == 0:
        return current_state

    best_state = current_state.copy()
    temp = self._initial_temp

    for i in range(self._max_iteration):
        next_state = self._create_next_state(current_state)
        if next_state.num_conflicts == 0:
            return next_state

        conflict_delta = current_state.num_conflicts - next_state.num_conflicts

        if conflict_delta > 0:
            current_state = next_state
            if next_state.num_conflicts < best_state.num_conflicts:
                best_state = next_state.copy()
        elif self._take_risk(conflict_delta, temp):
            current_state = next_state

        temp = self._calculate_temp(temp)
        if temp < 0.001:
            break

    return best_state
"""