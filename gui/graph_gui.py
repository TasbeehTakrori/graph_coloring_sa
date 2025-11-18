import tkinter as tk
from tkinter import ttk, messagebox

from models.graph import Graph
from algorithms.simulated_annealing import SimulatedAnnealing
from models.coloring_state import Coloring


class GraphGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Graph Coloring")

        self._graph = Graph()
        self._vertex_positions: dict[int, tuple[int, int]] = {}
        self._selected_vertex: int | None = None
        self._coloring_state: Coloring | None = None

        self._build_ui()
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        self._palette = [
            "#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF",
            "#A0C4FF", "#BDB2FF", "#FFC6FF", "#FFFFFC", "#CBF3F0",
            "#FFBF69", "#FF9F1C", "#2EC4B6", "#E71D36", "#FF595E",
            "#1982C4", "#6A4C93", "#8BBEB2", "#F7E1D7", "#FFCAE3"
        ]

    # ------------------------------------------------
    # Build UI
    # ------------------------------------------------
    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame, width=600, height=500, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        side_frame = ttk.Frame(main_frame, padding=10)
        side_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # ===== Mode selection =====
        ttk.Label(side_frame, text="Mode:").pack(anchor="w")

        self.mode_var = tk.StringVar(value="vertex")

        rb_vertex = ttk.Radiobutton(
            side_frame,
            text="Add Vertex",
            variable=self.mode_var,
            value="vertex"
        )
        rb_edge = ttk.Radiobutton(
            side_frame,
            text="Add Edge",
            variable=self.mode_var,
            value="edge"
        )

        rb_vertex.pack(anchor="w")
        rb_edge.pack(anchor="w")

        ttk.Separator(side_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # ===== SA Parameters =====
        ttk.Label(side_frame, text="Number of colors:").pack(anchor="w")
        self.num_colors_entry = ttk.Entry(side_frame)
        self.num_colors_entry.insert(0, "3")
        self.num_colors_entry.pack(anchor="w", fill=tk.X, pady=(0, 5))

        ttk.Label(side_frame, text="Max iterations:").pack(anchor="w")
        self.max_iter_entry = ttk.Entry(side_frame)
        self.max_iter_entry.insert(0, "1000")
        self.max_iter_entry.pack(anchor="w", fill=tk.X, pady=(0, 5))

        ttk.Label(side_frame, text="Initial temperature:").pack(anchor="w")
        self.init_temp_entry = ttk.Entry(side_frame)
        self.init_temp_entry.insert(0, "10.0")
        self.init_temp_entry.pack(anchor="w", fill=tk.X, pady=(0, 5))

        ttk.Label(side_frame, text="Cooling rate (0-1):").pack(anchor="w")
        self.cooling_entry = ttk.Entry(side_frame)
        self.cooling_entry.insert(0, "0.99")
        self.cooling_entry.pack(anchor="w", fill=tk.X, pady=(0, 10))

        # ===== Buttons: Randomize + Run SA + Reset =====
        random_btn = ttk.Button(
            side_frame,
            text="Randomize Colors",
            command=self._on_randomize
        )
        random_btn.pack(fill=tk.X, pady=5)

        run_btn = ttk.Button(
            side_frame,
            text="Run Simulated Annealing",
            command=self._on_run_sa
        )
        run_btn.pack(fill=tk.X, pady=5)

        reset_btn = ttk.Button(
            side_frame,
            text="Reset Graph",
            command=self._on_reset_graph
        )
        reset_btn.pack(fill=tk.X, pady=5)

        self.conflicts_var = tk.StringVar(value="Conflicts: -")
        ttk.Label(side_frame, textvariable=self.conflicts_var).pack(anchor="w", pady=(10, 0))

    # ------------------------------------------------
    # Main click controller
    # ------------------------------------------------
    def _on_canvas_click(self, event: tk.Event):
        mode = self.mode_var.get()
        x, y = event.x, event.y

        if mode == "vertex":
            self._handle_add_vertex(x, y)
        elif mode == "edge":
            self._handle_add_edge(x, y)

    # ------------------------------------------------
    # Handlers
    # ------------------------------------------------
    def _handle_add_vertex(self, x: int, y: int):
        self._graph.add_vertex()
        vertex_id = self._graph.vertex_count - 1
        self._vertex_positions[vertex_id] = (x, y)
        self._coloring_state = None
        self._redraw_all()
        self.conflicts_var.set("Conflicts: -")

    def _handle_add_edge(self, x: int, y: int):
        clicked = self._find_vertex_at(x, y)
        if clicked is None:
            return

        if self._selected_vertex is None:
            self._selected_vertex = clicked
            self._redraw_all(highlight=clicked)
            return

        v1 = self._selected_vertex
        v2 = clicked
        self._selected_vertex = None

        if v1 != v2:
            self._graph.add_edge(v1, v2)

        self._redraw_all()

    # ------------------------------------------------
    # Randomize Colors
    # ------------------------------------------------
    def _on_randomize(self):
        if self._graph.vertex_count == 0:
            messagebox.showinfo("Info", "Please add at least one vertex first.")
            return

        try:
            num_colors = int(self.num_colors_entry.get())
            if num_colors < 1:
                raise ValueError("Number of colors must be >= 1.")
            if num_colors > len(self._palette):
                messagebox.showinfo(
                    "Note",
                    f"Maximum unique colors is {len(self._palette)}.\n"
                    f"Extra colors will reuse the same palette."
                )

        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        coloring = Coloring(self._graph, num_colors)
        coloring.randomize()
        self._coloring_state = coloring

        coloring_dict = {
            v: coloring.get_color(v)
            for v in range(self._graph.vertex_count)
        }

        self._redraw_all(coloring=coloring_dict)
        self.conflicts_var.set(f"Conflicts (random): {coloring.num_conflicts}")

    # ------------------------------------------------
    # Run SA
    # ------------------------------------------------
    def _on_run_sa(self):

        if self._graph.vertex_count == 0:
            messagebox.showinfo("Info", "Please add at least one vertex.")
            return

        try:
            num_colors = int(self.num_colors_entry.get())
            max_iter = int(self.max_iter_entry.get())
            initial_temp = float(self.init_temp_entry.get())
            cooling_rate = float(self.cooling_entry.get())

            if num_colors < 1:
                raise ValueError("Number of colors must be >= 1.")
            if max_iter <= 0:
                raise ValueError("Max iterations must be > 0.")
            if initial_temp <= 0:
                raise ValueError("Initial temperature must be > 0.")
            if not (0 < cooling_rate < 1):
                raise ValueError("Cooling rate must be between 0 and 1.")
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        if (self._coloring_state is None) or (self._coloring_state.num_colors != num_colors):
            coloring_state = Coloring(self._graph, num_colors)
            coloring_state.randomize()
            self._coloring_state = coloring_state
        else:
            coloring_state = self._coloring_state

        sa = SimulatedAnnealing(
            graph=self._graph,
            max_iteration=max_iter,
            initial_temp=initial_temp,
            cooling_rate=cooling_rate,
            coloring_state= coloring_state
        )

        best_state: Coloring = sa.run()
        self._coloring_state = best_state

        coloring_dict = {
            v: best_state.get_color(v)
            for v in range(self._graph.vertex_count)
        }
        self._redraw_all(coloring=coloring_dict)

        self.conflicts_var.set(f"Conflicts (best): {best_state.num_conflicts}")

    # ------------------------------------------------
    # Reset graph
    # ------------------------------------------------
    def _on_reset_graph(self):
        self._graph = Graph()
        self._vertex_positions.clear()
        self._selected_vertex = None
        self.canvas.delete("all")
        self.conflicts_var.set("Conflicts: -")
        self._coloring_state = None

    # ------------------------------------------------
    # Drawing
    # ------------------------------------------------
    def _draw_vertex(self, vertex_id: int, color: str = "lightpink"):
        x, y = self._vertex_positions[vertex_id]
        r = 15

        self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=color, outline="black", width=2
        )
        self.canvas.create_text(x, y, text=str(vertex_id))

    def _draw_edge(self, v1: int, v2: int):
        x1, y1 = self._vertex_positions[v1]
        x2, y2 = self._vertex_positions[v2]

        self.canvas.create_line(x1, y1, x2, y2, width=2)

    def _redraw_all(self, highlight: int | None = None, coloring: dict[int, int] | None = None):
        self.canvas.delete("all")

        for v, neighbors in self._graph.adjacency_list.items():
            for n in neighbors:
                if v < n:
                    self._draw_edge(v, n)

        for v in range(self._graph.vertex_count):
            if coloring is not None and v in coloring:
                color_index = coloring[v]
                color = self._map_color_index_to_tk(color_index)
            else:
                color = "lightpink"

            if highlight is not None and v == highlight:
                color = "yellow"

            self._draw_vertex(v, color=color)

    # ------------------------------------------------
    # Helper: Find vertex by mouse position
    # ------------------------------------------------
    def _find_vertex_at(self, x: int, y: int, radius: int = 20):
        for v, (vx, vy) in self._vertex_positions.items():
            if (x - vx) ** 2 + (y - vy) ** 2 <= radius ** 2:
                return v
        return None

    def _map_color_index_to_tk(self, index: int) -> str:
        return self._palette[index % len(self._palette)]


def main():
    root = tk.Tk()
    app = GraphGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()