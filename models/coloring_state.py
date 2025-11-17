from models.graph import Graph


class Coloring:

    def __init__(self, graph: Graph, num_colors: int):
        self._graph = graph
        self._num_colors = num_colors
        self._colors = [0] * graph.vertex_count

    def set_color(self, vertex: int, color: int):
        self._colors[vertex] = color

    def get_colors(self) -> []:
        return self._colors

    def get_color(self, vertex: int) -> int:
        return self._colors[vertex]

    def compute_conflicts(self):

        adjacency_list = self._graph.adjacency_list
        num_conflicts = 0
        for v, neighbors in adjacency_list.items():
            for n in neighbors:
                if self._colors[v] == self._colors[n]:
                    num_conflicts+=1

        return num_conflicts//2





