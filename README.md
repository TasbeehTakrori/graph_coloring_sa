# Graph Coloring using Simulated Annealing

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
![Platform](https://img.shields.io/badge/Platform-Mac%20%7C%20Windows-lightgrey.svg)

**A visual interactive application for solving the Graph Coloring Problem using Simulated Annealing algorithm**

</div>

---

### 📖 Overview

This project implements an interactive visualization tool for solving the **Graph Coloring Problem** using the **Simulated Annealing** optimization technique. The application features a modern GUI built with Tkinter that allows users to create graphs, configure algorithm parameters, and watch the optimization process in real-time.

The Graph Coloring Problem is a classic NP-Hard combinatorial optimization problem where the objective is to assign colors to graph vertices such that no two adjacent vertices share the same color, while minimizing the total number of conflicts.

### ✨ Key Features

- 🎨 **Interactive Graph Editor**: Create custom graphs by adding vertices and edges through an intuitive point-and-click interface
- 🎲 **Random Graph Generator**: Generate random graphs with configurable vertex count and edge probability
- ⚙️ **Configurable SA Parameters**: Adjust initial temperature, cooling rate, max iterations, and number of colors
- 📊 **Real-time Visualization**: Watch the algorithm progress with live updates showing temperature and conflicts over time
- 📈 **Performance Metrics**: Track algorithm performance with matplotlib charts showing temperature decay and conflict reduction
- 🎬 **Animation Control**: Choose between animated step-by-step execution or instant solution
- 🎯 **Success Detection**: Automatic detection and celebration when a valid coloring (0 conflicts) is found
- 💾 **State Persistence**: Maintain coloring state between algorithm runs

### 🖼️ Screenshots

<img width="1024" height="786" alt="image" src="https://github.com/user-attachments/assets/2d9993df-0546-4dfa-9b34-c84041cb7ded" />

The application provides:
- Left panel:
   - Graph canvas with colorful vertex representation
   - Real-time charts showing temperature and conflicts evolution
- Right panel: Comprehensive controls for graph editing and algorithm configuration

---

## 🧩 Design & Best Practices Followed

Although this is a student project, the implementation follows several professional software engineering principles to keep the code **clean**, **maintainable**, and **extensible**:

### ✅ Separation of Concerns (SoC)
- The codebase is structured so each layer has a single responsibility:
  - `models/` handles graph representation and coloring logic  
  - `algorithms/` contains the Simulated Annealing optimizer  
  - `gui/` handles Tkinter visualization, events, and user interaction  
- This separation allows future algorithms (Genetic Algorithm, Tabu Search…) to be added without touching the GUI code.

### ✅ Clean Architecture Mindset
- The SA algorithm exposes a clear `step()` function that performs **exactly one iteration**, enabling:
  - Animated visualization using `root.after(...)`
  - Non-animated full execution using `run()`
- The GUI does **not** implement algorithm logic; it only orchestrates the process and updates the visualization.

### ✅ Encapsulation & Clear APIs
- `ColoringState` encapsulates:
  - vertex colors  
  - conflict counting  
  - neighbor modification  
- The GUI never manipulates raw lists or adjacency details—only through the class interface.

### ✅ Readability & Maintainability
- Small, focused methods  
- Descriptive variable names (`current_state`, `num_conflicts`, `cooling_rate`, etc.)
- Avoided global variables  
- No deeply nested logic, making the project easy to extend.

### ✅ Iterative Visual Updates (Non-blocking GUI)
- The animation uses Tkinter’s non-blocking scheduling (`root.after()`), ensuring:
  - Smooth visualization
  - GUI responsiveness during SA execution
  - Zero interference between GUI thread and algorithm logic

### ✅ Deterministic Random Graph Layout
- Random graphs are placed in a circular layout for:
  - Clean visualization  
  - Reproducible structure  
  - Avoiding overlapping vertices  

### ⭐ Overall Goal
The design aims to balance:
- Simplicity suitable for students  
- Clean architecture suitable for real-world projects  
- Flexibility to extend this tool in academic or research settings

---

### 📋 Requirements

```txt
Python 3.7+
tkinter (usually included with Python)
matplotlib>=3.3.0
```

### 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/TasbeehTakrori/graph_coloring_sa.git
cd graph_coloring_sa
```

2. **Install dependencies:**
```bash
pip install matplotlib
```

3. **Run the application:**
```bash
python gui/graph_gui.py
```

### 📖 Usage Guide

#### Creating a Graph

**Method 1: Manual Creation**
1. Select "Add Vertex" mode
2. Click on the canvas to add vertices
3. Select "Add Edge" mode
4. Click on two vertices to connect them with an edge

**Method 2: Random Generation**
1. Enter the number of vertices (e.g., 8)
2. Set edge probability (0-1, e.g., 0.3 means 30% chance for each edge)
3. Click "Generate random graph"

#### Running Simulated Annealing

1. **Configure Parameters:**
   - **Number of colors**: The color palette size (e.g., 3)
   - **Max iterations**: Maximum optimization steps (e.g., 1000)
   - **Initial temperature**: Starting temperature (e.g., 10.0)
   - **Cooling rate**: Temperature reduction factor 0-1 (e.g., 0.99)

2. **Set Visualization Options:**
   - Check "Animate SA" for step-by-step visualization
   - Set animation delay in milliseconds (lower = faster)

3. **Execute:**
   - Click "Randomize Colors" to generate an initial random coloring
   - Click "Run SA" to start the optimization
   - Click "Stop SA" to halt execution if needed

4. **View Results:**
   - Monitor current conflicts, iteration count, and temperature
   - Watch the graphs update in real-time
   - Canvas flashes green for successful coloring (0 conflicts)
   - Canvas flashes red if optimization completes with conflicts remaining

### 🧠 Algorithm Details

#### Simulated Annealing Overview

Simulated Annealing is a probabilistic optimization technique inspired by the metallurgical annealing process:

1. **Initialization**: Start with a random coloring and high temperature
2. **Iteration Loop**:
   - Generate a neighbor solution by changing one vertex's color
   - Calculate the change in conflicts (Δ)
   - Accept better solutions (Δ > 0) immediately
   - Accept worse solutions (Δ ≤ 0) with probability: `P = exp(Δ / T)`
3. **Cooling**: Reduce temperature: `T_new = cooling_rate × T_old`
4. **Termination**: Stop when:
   - A valid coloring is found (0 conflicts), or
   - Maximum iterations reached, or
   - Temperature drops below threshold (0.001)

#### Key Parameters

| Parameter | Description | Typical Range | Default |
|-----------|-------------|---------------|---------|
| `initial_temp` | Starting temperature (higher = more exploration) | 1.0 - 100.0 | 10.0 |
| `cooling_rate` | Temperature reduction factor | 0.90 - 0.99 | 0.99 |
| `max_iterations` | Maximum optimization steps | 100 - 10000 | 1000 |
| `num_colors` | Size of color palette | 2 - 20 | 3 |

#### Objective Function

The algorithm minimizes the number of conflicts, where a conflict occurs when two adjacent vertices share the same color:

```
Conflicts = Σ (edges where both vertices have same color)
```

### 📁 Project Structure

```
graph_coloring_sa/
├── GUI
│   └── gui.py                 # Main GUI application
├── models/
│   ├── graph.py               # Graph data structure (adjacency list)
│   └── coloring_state.py      # Coloring state management
├── algorithms/
│   └── simulated_annealing.py # SA implementation
└── README.md
```

### 🔧 Core Components

#### `Graph` Class
- Manages graph structure using adjacency list representation
- Methods: `add_vertex()`, `add_edge(v1, v2)`
- Properties: `vertex_count`, `adjacency_list`

#### `Coloring` Class
- Maintains color assignments for all vertices
- Methods: `randomize()`, `modify_one_vertex()`, `copy()`
- Automatically computes conflicts on state changes
- Properties: `num_conflicts`, `num_colors`

#### `SimulatedAnnealing` Class
- Implements the SA algorithm with step-by-step execution
- Methods: `run()` (complete execution), `step()` (single iteration)
- Tracks: `current_state`, `best_state`, `temperature`, `iteration`
- Records history: `temperature_history`, `conflicts_history`


### 🧪 Testing Tips

**For Easy Problems:**
- Use fewer vertices (5-8)
- Lower edge probability (0.2-0.3)
- Sufficient colors (3-4)
- Result: Usually finds valid coloring quickly

**For Challenging Problems:**
- More vertices (10-15)
- Higher edge probability (0.4-0.6)
- Fewer colors (2-3)
- May need higher initial temperature and more iterations

### 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 👤 Author

**Tasbeeh Takrori**
- GitHub: [@TasbeehTakrori](https://github.com/TasbeehTakrori)
- Project Link: [graph_coloring_sa](https://github.com/TasbeehTakrori/graph_coloring_sa)

---
