<h1 align="center">Clingo Dungeons</h1>

<p align="center">
  <strong>Declarative dungeon generation using Answer Set Programming</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+"></a>
  <a href="https://potassco.org/clingo/"><img src="https://img.shields.io/badge/clingo-5.7+-green.svg" alt="Clingo 5.7+"></a>
</p>

<p align="center">
  <img src="example_graph.png" alt="Dungeon Graph" width="600">
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

- **Graph**: Room topology with coordinates, dimensions, and content ([example](example_graph.png))
- **ASCII**: Text grid with Bresenham corridors ([example](example_ascii.txt))

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
