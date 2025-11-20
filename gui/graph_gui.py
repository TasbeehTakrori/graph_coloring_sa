import math
import random
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models.graph import Graph
from models.coloring_state import Coloring
from algorithms.simulated_annealing import SimulatedAnnealing


class GraphGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Graph Coloring – Simulated Annealing Visualizer")

        # Default canvas background color (for flash effect)
        self._canvas_bg_default = "#FAFAFA"

        # Graph model
        self._graph = Graph()
        self._vertex_positions: dict[int, tuple[int, int]] = {}
        self._selected_vertex: int | None = None
        self._coloring_state: Coloring | None = None

        # SA runtime
        self._sa: SimulatedAnnealing | None = None
        self._is_sa_running: bool = False

        # Animation options
        self.animate_var = tk.BooleanVar(value=True)     # Animate or instant
        self.animation_delay_var = tk.IntVar(value=20)   # delay in ms

        # Status labels (iteration, temp, conflicts)
        self.iteration_var = tk.StringVar(value="Iteration: -")
        self.temp_var = tk.StringVar(value="Temperature: -")
        self.conflicts_var = tk.StringVar(value="Conflicts: -")

        # Matplotlib objects
        self._fig = None
        self._ax_temp = None
        self._ax_conf = None
        self._plot_canvas = None

        # Histories for plots
        self._temp_history: list[float] = []
        self._conf_history: list[int] = []

        # Initialize styles
        self._init_style()

        # Build UI
        self._build_ui()
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Color palette
        self._palette = [
            "#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF",
            "#A0C4FF", "#BDB2FF", "#FFC6FF", "#FFFFFC", "#CBF3F0",
            "#FFBF69", "#FF9F1C", "#2EC4B6", "#E71D36", "#FF595E",
            "#1982C4", "#6A4C93", "#8BBEB2", "#F7E1D7", "#FFCAE3"
        ]

    # ------------------------------------------------
    # Styles (look & feel)
    # ------------------------------------------------
    def _init_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", font=("Consolas", 10))

        style.configure(
            "Success.TLabel",
            foreground="#2E7D32",
            font=("Consolas", 10, "bold")
        )

    # ------------------------------------------------
    # Build UI layout
    # ------------------------------------------------
    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ===== Left side: Title + Canvas + Plots (عموديًا) =====
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            left_frame,
            text="Graph Coloring using Simulated Annealing",
            style="Header.TLabel"
        )
        title_label.pack(anchor="center", pady=(0, 5))

        # Canvas في الأعلى
        self.canvas = tk.Canvas(
            left_frame,
            width=650,
            height=380,                       # قللنا الارتفاع قليلاً ليفسح مكان للـ plots
            bg=self._canvas_bg_default,
            highlightthickness=1,
            highlightbackground="#CCCCCC"
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Frame للمخططات تحت الـ canvas
        plots_frame = ttk.Frame(left_frame)
        plots_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(10, 5))

        # 1 row, 2 columns => المخططان بجانب بعض
        self._fig, axes = plt.subplots(
            1, 2, figsize=(8, 3.2), dpi=100  # زوّدنا العرض والارتفاع
        )
        self._ax_temp, self._ax_conf = axes

        self._ax_temp.set_title("Temperature Over Time")
        self._ax_temp.set_xlabel("Iteration")
        self._ax_temp.set_ylabel("Temperature")

        self._ax_conf.set_title("Conflicts Over Time")
        self._ax_conf.set_xlabel("Iteration")
        self._ax_conf.set_ylabel("Conflicts")

        self._fig.tight_layout()

        self._plot_canvas = FigureCanvasTkAgg(self._fig, master=plots_frame)
        self._plot_canvas.draw()
        self._plot_canvas.get_tk_widget().pack(fill=tk.X, expand=False)

        # ===== Right side: Controls panel =====
        side_frame = ttk.Frame(main_frame, padding=5)
        side_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # ========== Graph Editing Section ==========
        graph_frame = ttk.Labelframe(
            side_frame,
            text="Graph Editing",
            style="Section.TLabelframe"
        )
        graph_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(graph_frame, text="Mode:").grid(row=0, column=0, sticky="w", pady=(2, 4))

        self.mode_var = tk.StringVar(value="vertex")

        rb_vertex = ttk.Radiobutton(
            graph_frame,
            text="Add Vertex",
            variable=self.mode_var,
            value="vertex"
        )
        rb_edge = ttk.Radiobutton(
            graph_frame,
            text="Add Edge",
            variable=self.mode_var,
            value="edge"
        )

        rb_vertex.grid(row=1, column=0, sticky="w")
        rb_edge.grid(row=1, column=1, sticky="w")

        # ========== SA Parameters Section ==========
        params_frame = ttk.Labelframe(
            side_frame,
            text="Simulated Annealing Parameters",
            style="Section.TLabelframe"
        )
        params_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(params_frame, text="Number of colors:").grid(row=0, column=0, sticky="w")
        self.num_colors_entry = ttk.Entry(params_frame, width=8)
        self.num_colors_entry.insert(0, "3")
        self.num_colors_entry.grid(row=0, column=1, sticky="we", pady=2, padx=(5, 0))

        ttk.Label(params_frame, text="Max iterations:").grid(row=1, column=0, sticky="w")
        self.max_iter_entry = ttk.Entry(params_frame, width=8)
        self.max_iter_entry.insert(0, "1000")
        self.max_iter_entry.grid(row=1, column=1, sticky="we", pady=2, padx=(5, 0))

        ttk.Label(params_frame, text="Initial temperature:").grid(row=2, column=0, sticky="w")
        self.init_temp_entry = ttk.Entry(params_frame, width=8)
        self.init_temp_entry.insert(0, "10.0")
        self.init_temp_entry.grid(row=2, column=1, sticky="we", pady=2, padx=(5, 0))

        ttk.Label(params_frame, text="Cooling rate (0-1):").grid(row=3, column=0, sticky="w")
        self.cooling_entry = ttk.Entry(params_frame, width=8)
        self.cooling_entry.insert(0, "0.99")
        self.cooling_entry.grid(row=3, column=1, sticky="we", pady=(2, 4), padx=(5, 0))

        params_frame.columnconfigure(1, weight=1)

        # ========== Animation Options Section ==========
        animation_frame = ttk.Labelframe(
            side_frame,
            text="Visualization Options",
            style="Section.TLabelframe"
        )
        animation_frame.pack(fill=tk.X, pady=(0, 8))

        animate_check = ttk.Checkbutton(
            animation_frame,
            text="Animate SA",
            variable=self.animate_var
        )
        animate_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        ttk.Label(animation_frame, text="Animation delay (ms):").grid(row=1, column=0, sticky="w")
        self.delay_entry = ttk.Entry(animation_frame, textvariable=self.animation_delay_var, width=8)
        self.delay_entry.grid(row=1, column=1, sticky="we", pady=(0, 2), padx=(5, 0))

        animation_frame.columnconfigure(1, weight=1)

        # ========== Controls Section ==========
        controls_frame = ttk.Labelframe(
            side_frame,
            text="Controls",
            style="Section.TLabelframe"
        )
        controls_frame.pack(fill=tk.X, pady=(0, 8))

        random_btn = ttk.Button(
            controls_frame,
            text="Randomize Colors",
            command=self._on_randomize
        )
        random_btn.grid(row=0, column=0, sticky="we", pady=2)

        self.run_btn = ttk.Button(
            controls_frame,
            text="Run SA",
            command=self._on_run_sa
        )
        self.run_btn.grid(row=1, column=0, sticky="we", pady=2)

        self.stop_btn = ttk.Button(
            controls_frame,
            text="Stop SA",
            command=self._on_stop_sa
        )
        self.stop_btn.grid(row=2, column=0, sticky="we", pady=2)

        reset_btn = ttk.Button(
            controls_frame,
            text="Reset Graph",
            command=self._on_reset_graph
        )
        reset_btn.grid(row=3, column=0, sticky="we", pady=(2, 4))

        # ----- Random graph controls -----
        ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(
            row=4, column=0, sticky="we", pady=(4, 4)
        )

        random_graph_frame = ttk.Frame(controls_frame)
        random_graph_frame.grid(row=5, column=0, sticky="we")

        ttk.Label(random_graph_frame, text="Random graph:").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        ttk.Label(random_graph_frame, text="Vertices:").grid(row=1, column=0, sticky="w")
        self.random_vertices_entry = ttk.Entry(random_graph_frame, width=6)
        self.random_vertices_entry.insert(0, "8")
        self.random_vertices_entry.grid(row=1, column=1, sticky="we", pady=(0, 2))

        ttk.Label(random_graph_frame, text="Edge prob (0-1):").grid(row=2, column=0, sticky="w")
        self.random_prob_entry = ttk.Entry(random_graph_frame, width=6)
        self.random_prob_entry.insert(0, "0.3")
        self.random_prob_entry.grid(row=2, column=1, sticky="we", pady=(0, 4))

        random_graph_frame.columnconfigure(1, weight=1)

        gen_btn = ttk.Button(
            random_graph_frame,
            text="Generate random graph",
            command=self._on_generate_random_graph
        )
        gen_btn.grid(row=3, column=0, columnspan=2, sticky="we")

        controls_frame.columnconfigure(0, weight=1)

        # ========== Status Section ==========
        status_frame = ttk.Labelframe(
            side_frame,
            text="SA Status",
            style="Section.TLabelframe"
        )
        status_frame.pack(fill=tk.X, pady=(0, 8))

        self.conflicts_var_label = ttk.Label(
            status_frame,
            textvariable=self.conflicts_var,
            style="Status.TLabel"
        )
        self.conflicts_var_label.grid(row=0, column=0, sticky="w", pady=2)

        ttk.Label(
            status_frame,
            textvariable=self.iteration_var,
            style="Status.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=2)

        ttk.Label(
            status_frame,
            textvariable=self.temp_var,
            style="Status.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=(2, 4))

    # ------------------------------------------------
    # Canvas click handlers
    # ------------------------------------------------
    def _on_canvas_click(self, event: tk.Event):
        if self._is_sa_running:
            return

        mode = self.mode_var.get()
        x, y = event.x, event.y

        if mode == "vertex":
            self._handle_add_vertex(x, y)
        elif mode == "edge":
            self._handle_add_edge(x, y)

    def _handle_add_vertex(self, x: int, y: int):
        self._graph.add_vertex()
        vertex_id = self._graph.vertex_count - 1
        self._vertex_positions[vertex_id] = (x, y)
        self._coloring_state = None
        self._redraw_all()

        # Reset status
        self.conflicts_var.set("Conflicts: -")
        self.iteration_var.set("Iteration: -")
        self.temp_var.set("Temperature: -")
        self._set_conflicts_success(False)
        self._clear_plots()

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
    # Random graph
    # ------------------------------------------------
    def _on_generate_random_graph(self):
        if self._is_sa_running:
            messagebox.showwarning("Warning", "Cannot change graph while SA is running.")
            return

        try:
            n_vertices = int(self.random_vertices_entry.get())
            edge_prob = float(self.random_prob_entry.get())

            if n_vertices <= 0:
                raise ValueError("Number of vertices must be > 0.")
            if not (0.0 <= edge_prob <= 1.0):
                raise ValueError("Edge probability must be between 0 and 1.")
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        # Reset graph
        self._graph = Graph()
        self._vertex_positions.clear()
        self._selected_vertex = None
        self._coloring_state = None
        self.canvas.delete("all")
        self._temp_history.clear()
        self._conf_history.clear()
        self._clear_plots()
        self.conflicts_var.set("Conflicts: -")
        self.iteration_var.set("Iteration: -")
        self.temp_var.set("Temperature: -")
        self._set_conflicts_success(False)

        # Place vertices on a circle
        width = int(self.canvas.winfo_width() or 650)
        height = int(self.canvas.winfo_height() or 380)
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 2 - 40

        for i in range(n_vertices):
            self._graph.add_vertex()
            angle = 2 * math.pi * i / n_vertices
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            self._vertex_positions[i] = (x, y)

        # Random edges
        for i in range(n_vertices):
            for j in range(i + 1, n_vertices):
                if random.random() < edge_prob:
                    self._graph.add_edge(i, j)

        self._redraw_all()

    # ------------------------------------------------
    # Randomize colors
    # ------------------------------------------------
    def _on_randomize(self):
        if self._is_sa_running:
            return

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
        self.iteration_var.set("Iteration: -")
        self.temp_var.set("Temperature: -")
        self._set_conflicts_success(False)
        self._clear_plots()

    # ------------------------------------------------
    # Run SA (animate or instant)
    # ------------------------------------------------
    def _on_run_sa(self):
        if self._is_sa_running:
            messagebox.showinfo("Info", "Simulated Annealing is already running.")
            return

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

        # Initial coloring
        if (self._coloring_state is None) or (self._coloring_state.num_colors != num_colors):
            coloring_state = Coloring(self._graph, num_colors)
            coloring_state.randomize()
            self._coloring_state = coloring_state
        else:
            coloring_state = self._coloring_state

        # Create SA object
        self._sa = SimulatedAnnealing(
            graph=self._graph,
            coloring_state=coloring_state,
            max_iteration=max_iter,
            initial_temp=initial_temp,
            cooling_rate=cooling_rate
        )

        # reset histories for plots
        self._temp_history.clear()
        self._conf_history.clear()
        self._clear_plots()

        self._is_sa_running = True
        self.run_btn.config(state=tk.DISABLED)
        self._set_conflicts_success(False)

        # Reset status display
        self.iteration_var.set(f"Iteration: 0 / {max_iter}")
        self.temp_var.set(f"Temperature: {initial_temp:.4f}")
        self.conflicts_var.set(f"Conflicts (current): {self._sa.current_state.num_conflicts}")

        if self.animate_var.get():
            self._animate_sa_step()
        else:
            best_state = self._sa.run()
            self._coloring_state = best_state
            # history في هذا الوضع غير متتبَّعة خطوة بخطوة، نعرض فقط النهاية
            self._finish_sa(best_state)
            self._is_sa_running = False
            self.run_btn.config(state=tk.NORMAL)
            self._sa = None

    # ------------------------------------------------
    # Stop SA
    # ------------------------------------------------
    def _on_stop_sa(self):
        if not self._is_sa_running:
            return
        self._sa = None
        self._is_sa_running = False
        self.run_btn.config(state=tk.NORMAL)
        self.conflicts_var.set("Conflicts: (stopped)")
        self._set_conflicts_success(False)

    # ------------------------------------------------
    # Animation loop
    # ------------------------------------------------
    def _animate_sa_step(self):
        if self._sa is None:
            self._is_sa_running = False
            self.run_btn.config(state=tk.NORMAL)
            return

        finished = self._sa.step()

        current_state = self._sa.current_state
        coloring_dict = {
            v: current_state.get_color(v)
            for v in range(self._graph.vertex_count)
        }
        self._redraw_all(coloring=coloring_dict)

        # Update status
        self.conflicts_var.set(f"Conflicts (current): {current_state.num_conflicts}")
        self.iteration_var.set(
            f"Iteration: {self._sa.iteration} / {self._sa._max_iteration}"
        )
        self.temp_var.set(f"Temperature: {self._sa.temp:.4f}")

        # Update histories & plots
        self._temp_history.append(self._sa.temp)
        self._conf_history.append(current_state.num_conflicts)
        self._update_sa_plots(self._temp_history, self._conf_history)

        if not finished:
            try:
                delay = int(self.animation_delay_var.get())
                if delay < 1:
                    delay = 1
            except ValueError:
                delay = 20
            self.root.after(delay, self._animate_sa_step)
        else:
            best_state = self._sa.best_state
            self._coloring_state = best_state
            self._finish_sa(best_state)

            self._is_sa_running = False
            self.run_btn.config(state=tk.NORMAL)
            self._sa = None

    # ------------------------------------------------
    # Finish SA (common for instant & animated)
    # ------------------------------------------------
    def _finish_sa(self, best_state: Coloring):
        best_coloring = {
            v: best_state.get_color(v)
            for v in range(self._graph.vertex_count)
        }
        self._redraw_all(coloring=best_coloring)

        if best_state.num_conflicts == 0:
            self.conflicts_var.set("Conflicts (best): 0")
            self._set_conflicts_success(True)
            self._flash_canvas_success()
            messagebox.showinfo("Solution Found", "A proper coloring with 0 conflicts was found!")
        else:
            self.conflicts_var.set(f"Conflicts (best): {best_state.num_conflicts}")
            self._set_conflicts_success(False)
            self._flash_canvas_failure()
            messagebox.showwarning(
                "No Perfect Solution",
                f"Simulated Annealing stopped with {best_state.num_conflicts} conflicts.\n"
                f"This is the best solution it found under the given parameters."
            )

        # في حالة الـ animation، الـ history جاهزة؛ في حالة non-animated، ما في history تقريبًا
        self._update_sa_plots(self._temp_history, self._conf_history)

    # ------------------------------------------------
    # Plot helpers
    # ------------------------------------------------
    def _clear_plots(self):
        self._update_sa_plots([], [])

    def _update_sa_plots(self, temps: list[float], conflicts: list[int]):
        # Clear axes
        self._ax_temp.clear()
        self._ax_conf.clear()

        self._ax_temp.set_title("Temperature Over Time")
        self._ax_temp.set_xlabel("Iteration")
        self._ax_temp.set_ylabel("Temperature")

        self._ax_conf.set_title("Conflicts Over Time")
        self._ax_conf.set_xlabel("Iteration")
        self._ax_conf.set_ylabel("Conflicts")

        if temps and conflicts:
            iterations = list(range(len(temps)))
            self._ax_temp.plot(iterations, temps)
            self._ax_conf.plot(iterations, conflicts)

        self._fig.tight_layout()
        self._plot_canvas.draw_idle()

    # ------------------------------------------------
    # Visual helpers (success styling & canvas flash)
    # ------------------------------------------------
    def _set_conflicts_success(self, is_success: bool):
        if is_success:
            self.conflicts_var_label.configure(style="Success.TLabel")
        else:
            self.conflicts_var_label.configure(style="Status.TLabel")

    def _flash_canvas_success(self):
        success_bg = "#A5D6A7"
        self.canvas.configure(bg=success_bg)
        self.canvas.update_idletasks()
        self.root.after(700, lambda: self.canvas.configure(bg=self._canvas_bg_default))

    def _flash_canvas_failure(self):
        fail_bg = "#ED5F40"
        self.canvas.configure(bg=fail_bg)
        self.canvas.update_idletasks()
        self.root.after(700, lambda: self.canvas.configure(bg=self._canvas_bg_default))

    # ------------------------------------------------
    # Reset graph
    # ------------------------------------------------
    def _on_reset_graph(self):
        if self._is_sa_running:
            return

        self._graph = Graph()
        self._vertex_positions.clear()
        self._selected_vertex = None
        self.canvas.delete("all")
        self._coloring_state = None
        self._sa = None

        self.canvas.configure(bg=self._canvas_bg_default)
        self.conflicts_var.set("Conflicts: -")
        self.iteration_var.set("Iteration: -")
        self.temp_var.set("Temperature: -")
        self._set_conflicts_success(False)
        self._temp_history.clear()
        self._conf_history.clear()
        self._clear_plots()

    # ------------------------------------------------
    # Drawing helpers
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

    def _redraw_all(self,
                    highlight: int | None = None,
                    coloring: dict[int, int] | None = None):
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