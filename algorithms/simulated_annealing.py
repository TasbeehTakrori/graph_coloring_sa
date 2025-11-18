import math
import random
from models.coloring_state import Coloring
from models.graph import Graph

class SimulatedAnnealing:

    def __init__(self, graph: Graph, coloring_state: Coloring, max_iteration: int, initial_temp: float, cooling_rate : float):
        self._graph = graph
        self._max_iteration = max_iteration
        self._initial_temp = initial_temp
        self._cooling_rate = cooling_rate
        self._coloring_state = coloring_state

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

            conflict_delta =  current_state.num_conflicts - next_state.num_conflicts

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

    def _create_next_state(self, coloring_state : Coloring) -> Coloring:
        state = coloring_state.copy()
        state.modify_one_vertex()
        return state

    def _take_risk(self, conflict_delta : int, temp : float) -> bool:
        if conflict_delta > 0 or temp == 0:
            return False
        probability = math.exp(conflict_delta/temp)
        return probability > random.random()

    def _calculate_temp(self, temp: float):
        return self._cooling_rate * temp










