import random
from models.graph import Graph
from models.coloring_state import Coloring
from algorithms.simulated_annealing import SimulatedAnnealing


def create_triangle_graph() -> Graph:
    g = Graph()
    for _ in range(3):
        g.add_vertex()

    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(0, 2)
    return g


def test_sa_reduces_conflicts_on_triangle():
    random.seed(0)

    graph = create_triangle_graph()
    num_colors = 3

    # Create initial coloring
    initial_coloring = Coloring(graph, num_colors)
    initial_coloring.randomize()
    initial_conflicts = initial_coloring.num_conflicts

    # Pass coloring_state instead of num_colors
    sa = SimulatedAnnealing(
        graph=graph,
        coloring_state=initial_coloring,
        max_iteration=1000,
        initial_temp=10.0,
        cooling_rate=0.99
    )

    result_coloring = sa.run()
    final_conflicts = result_coloring.num_conflicts

    print("Initial conflicts:", initial_conflicts)
    print("Final conflicts:", final_conflicts)

    assert 0 <= final_conflicts <= initial_conflicts