from models.coloring_state import Coloring
from models.graph import Graph


def test_conflicts():
    g = Graph()
    for i in range(3):
        g.add_vertex()

    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(0, 2)

    c = Coloring(g, num_colors=2)

    c.set_color(0, 0)
    c.set_color(1, 0)
    c.set_color(2, 1)

    assert c._num_conflicts == 1

