from models.coloring_state import Coloring
from models.graph import Graph


class SimulatedAnnealing:

    def __init__(self, graph: Graph, num_colors: int, max_iteration: int, initial_temp: int):
        self._graph = graph
        self._num_colors = num_colors
        self._max_iteration = max_iteration
        self._initial_temp = initial_temp

    def run(self) -> Coloring:

        current_state = self._create_initial_state()
        if current_state.num_conflicts == 0:
            return current_state

        best_state = current_state.copy()
        temp = self._initial_temp

        for i in range(self._max_iteration):
            next_state = self._create_next_state(current_state)
            conflict_delta =  next_state.num_conflicts - current_state.num_conflicts

            if conflict_delta < 0:
                current_state = next_state
                if next_state.num_conflicts < best_state.num_conflicts:
                    best_state = next_state.copy()
            elif self._take_risk(conflict_delta, temp):
                current_state = next_state

            temp = self._calculate_temp(i,temp)
        return best_state

    def _create_initial_state(self):
        coloring = Coloring(graph = self._graph, num_colors = self._num_colors)
        coloring.randomize()
        return coloring

    def _create_next_state(self, coloring_state : Coloring) -> Coloring:
        state = coloring_state.copy()
        state.modify_one_vertex()
        return state

    def _take_risk(self, conflict_delta : int, temp : float) -> bool:


    # To do list
    # 1. complete take risk function
    # 2. update (modify one vertex) function, to avoid repeat the same color













