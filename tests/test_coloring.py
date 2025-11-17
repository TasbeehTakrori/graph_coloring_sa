import  random

from models.coloring_state import Coloring
from models.graph import Graph

def create_triangle_graph() -> Graph:
    g = Graph()
    for _ in range(3):
        g.add_vertex()

    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(0, 2)
    return g


def test_conflicts_on_triangle():
    graph = create_triangle_graph()
    coloring = Coloring(graph, num_colors=3)

    coloring.set_color(0, 0)
    coloring.set_color(1, 0)
    coloring.set_color(2, 0)

    assert coloring.num_conflicts == 3

    coloring.set_color(0, 0)
    coloring.set_color(1, 1)
    coloring.set_color(2, 2)

    assert coloring.num_conflicts == 0


def test_modify_one_vertex_changes_at_least_one_color():
    random.seed(0)

    graph = create_triangle_graph()
    coloring = Coloring(graph, num_colors=3)
    coloring.randomize()

    before = coloring.get_colors()
    coloring.modify_one_vertex()
    after = coloring.get_colors()

    assert before != after