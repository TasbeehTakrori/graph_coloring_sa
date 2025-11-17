import random

from models.graph import Graph


class Coloring:

    def __init__(self, graph: Graph, num_colors: int):
        self._graph = graph
        self._num_colors = num_colors
        self._colors = [0] * graph.vertex_count
        self._num_conflicts = 0
        self._compute_conflicts()

    @property
    def num_conflicts(self):
        return self._num_conflicts

    def set_color(self, vertex: int, color: int):
        self._colors[vertex] = color
        self._compute_conflicts()


    def get_colors(self) -> list[int]:
        return self._colors

    def get_color(self, vertex: int) -> int:
        return self._colors[vertex]

    def _compute_conflicts(self):

        adjacency_list = self._graph.adjacency_list
        num_conflicts = 0
        for v, neighbors in adjacency_list.items():
            for n in neighbors:
                if self._colors[v] == self._colors[n]:
                    num_conflicts+=1

        self._num_conflicts = num_conflicts//2

    def randomize(self):
        for i in range(len(self._colors)):
            self._colors[i] = random.randint(0, self._num_colors - 1)

        self._compute_conflicts()

    def copy(self):
        new_coloring = Coloring(self._graph, self._num_colors)
        new_coloring._colors = self._colors.copy()
        new_coloring._num_conflicts = self._num_conflicts
        return new_coloring

    def modify_one_vertex(self):
        random_vertex = random.randint(0, len(self._colors)-1)
        current_color = self._colors[random_vertex]
        new_color = random.randint(0, self._num_colors - 1)
        while new_color == current_color:  #to avoid stay same color
            new_color = random.randint(0, self._num_colors - 1)

        self._colors[random_vertex] = new_color
        self._compute_conflicts()
