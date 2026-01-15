# Contributing to Clingo Dungeons

First off, **thank you** for considering contributing! I truly believe in open source and the power of community collaboration. Unlike many repositories, I actively welcome contributions of all kinds - from bug fixes to new features.

## My Promise to Contributors

- **I will respond to every PR and issue** - I guarantee feedback on all contributions
- **Bug fixes are obvious accepts** - If it fixes a bug, it's getting merged
- **New features are welcome** - I'm genuinely open to new ideas and enhancements
- **Direct line of communication** - If I'm not responding to a PR or issue, email me directly at johnvondrashek@gmail.com

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Open a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version)
   - Sample ASP rules if applicable

### Suggesting Features

I'm open to new features! When proposing:

- Explain the problem you're trying to solve
- Describe your proposed solution
- Consider how it fits with declarative dungeon generation
- Bonus points for ASCII mockups of expected output

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes: `uv run python generate_examples.py`
5. Commit with clear messages
6. Push and open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/clingo-dungeons.git
cd clingo-dungeons

# Install dependencies
uv sync

# Generate test dungeons
uv run python generate_examples.py

# Run individual generators
uv run python pmd/render_ascii.py 7
uv run python pmd/visualize_graph.py 7 test.png
```

### Tech Stack

- **Python 3.12+** - Runtime
- **Clingo 5.7+** - Answer Set Programming solver
- **NetworkX** - Graph algorithms and force-directed layout
- **Matplotlib** - PNG visualization
- **uv** - Package management

### Project Structure

```
clingo-dungeons/
├── pmd/
│   ├── floor_clingcon_full.lp  # ASP dungeon constraints
│   ├── generate_clingcon.py    # Clingo runner & output parser
│   ├── visualize_graph.py      # PNG graph visualization
│   └── render_ascii.py         # ASCII grid renderer
├── generate_examples.py        # Batch generation script
└── output/                     # Generated examples
```

### Your First Contribution

Some good starting points:

- Adding new room types (treasure rooms, boss rooms)
- New content types (items, enemies, traps)
- Additional ASP constraints (room adjacency rules, critical paths)
- Improving corridor routing algorithms
- Alternative output formats (JSON, Tiled TMX)

Resources for first-time contributors:
- http://makeapullrequest.com/
- https://www.firsttimersonly.com/

## Code Style

This project values bold, elegant solutions over verbose "safe" code:

- **Density over sprawl** - 50 brilliant lines beat 500 obvious ones
- **Names are documentation** - if you need a comment, you need a better name
- **State is liability** - every variable is a burden; justify each one

Don't be afraid to propose refactors if you see a better way.

## Code of Conduct

This project follows the [Rule of St. Benedict](CODE_OF_CONDUCT.md) as its code of conduct.

## Questions?

- Open an issue
- Email: johnvondrashek@gmail.com

---

*Thank you for helping make declarative dungeon generation better for everyone!*
