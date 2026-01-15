<h1 align="center">Clingo Dungeons</h1>

<p align="center">
  <strong>Declarative dungeon generation using Answer Set Programming</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+"></a>
  <a href="https://potassco.org/clingo/"><img src="https://img.shields.io/badge/clingo-5.7+-green.svg" alt="Clingo 5.7+"></a>
</p>

---

Generate roguelike dungeon layouts using Clingo (Answer Set Programming). Define constraints declaratively - room counts, connectivity rules, content distribution - and let the solver find valid configurations. Then render to ASCII or graph visualizations.

## Features

- **Declarative Constraints** - Define what you want, not how to build it
- **Room Topology** - Configurable room counts, sizes (4x4 to 8x8), and connection limits
- **Content Distribution** - Items, enemies, and traps placed according to rules
- **Force-Directed Layout** - Physics-based room positioning with minimum gaps
- **Bresenham Corridors** - Diagonal-approximating paths between rooms
- **Multiple Outputs** - ASCII text grids and PNG graph visualizations

## Installation

```bash
# Clone the repository
git clone https://github.com/JohnVonDrashek/clingo-dungeons.git
cd clingo-dungeons

# Install dependencies with uv
uv sync
```

## Quick Start

**Generate example dungeons:**

```bash
uv run python generate_examples.py
```

This creates 10 dungeons in `output/`:
- `output/graph/` - PNG visualizations of room topology
- `output/ascii/` - ASCII text grid layouts

**Generate a single ASCII dungeon:**

```bash
uv run python pmd/render_ascii.py 7
```

**Generate a graph visualization:**

```bash
uv run python pmd/visualize_graph.py 7 dungeon.png
```

## Example Output

**ASCII Grid:**
```
    ....
    ....
    ....        ........
      ,         ........
     ,          ....S...,
.....,                  ,    .....
.....,                   ,   .....
..>..                    ,,,,.....
....                          ....
```

**Graph Visualization:**

Rooms shown on a grid with coordinates, dimensions, and content counts. Spawn (green), Stairs (orange), and regular rooms (blue) connected by corridors.

## How It Works

### 1. Topology Generation (Clingo)

The ASP solver generates valid dungeon configurations:

```prolog
% 7 rooms, each gets a grid position
room(1..num_rooms).
{ room_gx(R, X) : grid_pos(X) } = 1 :- room(R).
{ room_gy(R, Y) : grid_pos(Y) } = 1 :- room(R).

% Connected rooms must be close (Manhattan distance ≤ 2)
:- corridor(R1, R2), grid_dist(R1, R2, D), D > 2.

% All rooms reachable from spawn
reachable(R) :- is_spawn(R).
reachable(R2) :- reachable(R1), edge(R1, R2).
:- room(R), not reachable(R).
```

### 2. Force-Directed Placement (NetworkX)

Rooms are positioned using spring layout physics:
- Connected rooms attract
- All rooms repel
- Minimum 2-tile gap enforced

### 3. Corridor Routing (Bresenham)

Corridors approximate diagonal lines using Bresenham's algorithm, falling back to A* pathfinding when blocked.

## Configuration

Edit `pmd/floor_clingcon_full.lp` to change dungeon parameters:

```prolog
#const num_rooms = 7.      % Number of rooms
#const num_items = 4.      % Items to place
#const num_enemies = 5.    % Enemies to place
#const num_traps = 2.      % Traps to place
#const grid_size = 4.      % Coarse grid (4x4)
#const min_room_size = 4.  % Minimum room dimension
#const max_room_size = 8.  % Maximum room dimension
```

## Project Structure

```
clingo-dungeons/
├── pmd/
│   ├── floor_clingcon_full.lp  # ASP dungeon rules
│   ├── generate_clingcon.py    # Clingo runner & parser
│   ├── visualize_graph.py      # PNG graph output
│   └── render_ascii.py         # ASCII grid output
├── generate_examples.py        # Batch generation script
└── output/
    ├── graph/                  # PNG visualizations
    └── ascii/                  # ASCII text files
```

## Dependencies

- **Python 3.12+**
- **Clingo 5.7+** - Answer Set Programming solver
- **NetworkX** - Graph algorithms and force-directed layout
- **NumPy** - Numerical operations
- **Matplotlib** - PNG visualization

## Why ASP?

Answer Set Programming excels at constraint satisfaction:

- **Declarative** - Describe valid dungeons, don't code generation algorithms
- **Complete** - Solver explores all possibilities, finds valid solutions
- **Flexible** - Add new constraints without rewriting logic
- **Debuggable** - Unsatisfiable constraints give clear feedback

## License

MIT License - see [LICENSE](LICENSE) for details.

## Code of Conduct

This project follows the [Rule of St. Benedict](CODE_OF_CONDUCT.md).

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
