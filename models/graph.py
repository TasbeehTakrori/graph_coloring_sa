
class Graph:
    def __init__(self) -> None:
        self._adjacency_list = {}
        self._vertex_count = 0

    @property
    def vertex_count(self) -> int:
        return self._vertex_count

    def _is_same_vertex(self, first_vertex : int, second_vertex: int) -> bool:
        return first_vertex == second_vertex

    def add_vertex(self) -> None:
        new_id = self._vertex_count
        self._adjacency_list[new_id] = []
        self._vertex_count += 1

    def _vertices_exist(self, first_vertex : int, second_vertex: int) -> bool:
        return (first_vertex in self._adjacency_list) and (second_vertex in self._adjacency_list)


    def add_edge(self, first_vertex : int, second_vertex: int) -> None:

        if self._is_same_vertex(first_vertex,second_vertex):
            return

        if not self._vertices_exist(first_vertex, second_vertex):
            return

        adj_first = self._adjacency_list[first_vertex]
        adj_second = self._adjacency_list[second_vertex]

        if first_vertex not in adj_second:
            adj_second.append(first_vertex)

        if second_vertex not in adj_first:
            adj_first.append(second_vertex)








