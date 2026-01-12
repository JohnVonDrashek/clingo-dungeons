# Clingo Dungeon Generation Toolkit - Design

## Purpose

Explore where Answer Set Programming (clingo) is appropriate in roguelike dungeon generation and where it isn't. Primary focus: **expressiveness** - can complex dungeon rules be expressed more naturally in ASP than procedural code?

Secondary concerns: performance and output quality.

## Approach: Layer-by-Layer Modules

Build independent .lp modules for each generation layer, each with its own test harness. This isolates where clingo shines vs struggles.

## Project Structure

```
clingo-dungeons/
├── pyproject.toml          # uv project, clingo dependency
├── runner.py               # Thin wrapper: load .lp, solve, parse output
├── graph/
│   ├── topology.lp         # Room count, connection rules
│   ├── critical_path.lp    # Spawn → boss path constraints
│   └── test_graph.py       # Generate and visualize graph solutions
├── placement/
│   ├── rooms.lp            # Room dimensions, position bounds
│   ├── non_overlap.lp      # No two rooms share tiles
│   ├── corridors.lp        # Path routing between connected rooms
│   └── test_placement.py   # Visualize placed dungeons as ASCII/PNG
├── content/
│   ├── items.lp            # Item placement rules
│   ├── enemies.lp          # Enemy distribution, difficulty curve
│   ├── keys_locks.lp       # Key must be reachable before its lock
│   └── test_content.py     # Validate and visualize content placement
├── examples/
│   └── full_dungeon.py     # Composed example using all layers
└── docs/plans/
    └── this file
```

## Layer 1: Graph (Expected: Strong Fit)

Dungeon topology is pure constraint satisfaction.

**Inputs:** Number of rooms, connection density, special room types (spawn, boss, shop)

**Constraints:**
- Graph must be connected
- Boss room at max distance from spawn
- Optional branching factor limits

**Output:** `room(1..N)`, `connects(R1, R2)`, `room_type(R, Type)`

**Example constraint:**
```prolog
% Every room must be reachable from spawn
reachable(R) :- room_type(R, spawn).
reachable(R2) :- reachable(R1), connects(R1, R2).
:- room(R), not reachable(R).
```

## Layer 2: Placement (Expected: Performance Challenge)

2D geometry with non-overlap constraints.

**Inputs:** Graph from previous layer, room size ranges, grid bounds

**Constraints:**
- Rooms don't overlap
- Corridors connect doorways
- Corridors don't cross rooms

**Output:** `room_pos(R, X, Y)`, `room_size(R, W, H)`, `corridor(R1, R2, PathTiles...)`

**Example constraint:**
```prolog
% No overlap: if two rooms share any tile, reject
:- room(R1), room(R2), R1 < R2,
   room_pos(R1, X1, Y1), room_size(R1, W1, H1),
   room_pos(R2, X2, Y2), room_size(R2, W2, H2),
   X1 < X2 + W2, X2 < X1 + W1,
   Y1 < Y2 + H2, Y2 < Y1 + H1.
```

**Performance concern:** Grounding all possible positions on large grids is expensive.

**Mitigation ideas:**
- Constrain rooms to coarse grid first
- Use clingo optimization to minimize wasted space
- Compare solve time vs BSP/random placement

## Layer 3: Content (Expected: Strong Fit)

Pure logic constraints without geometry.

**Inputs:** Room graph with distances, room sizes/types

**Constraints:**
- Key appears in room reachable before locked door
- Boss room has specific item rules
- Difficulty increases along critical path
- Treasure rooms have higher item density

**Output:** `item_at(Item, Room)`, `enemy_at(EnemyType, Room)`, `locked_door(R1, R2, KeyColor)`

**Example - key-before-lock:**
```prolog
% Key must be in a room reachable without passing through its lock
key_reachable(K, R) :- key_at(K, R).
key_reachable(K, R2) :- key_reachable(K, R1), connects(R1, R2),
                        not locked_door(R1, R2, K).
:- locked_door(R1, R2, K), not key_reachable(K, R1).
```

## Python Runner

Minimal wrapper - clingo does the work, Python handles I/O:

```python
def solve(lp_files: list[str], num_solutions=1) -> list[dict]
def parse_atoms(model) -> dict
def render_ascii(placement_result) -> str
```

No business logic in Python. Constraint logic belongs in .lp files.

## Composition Modes

1. **Chained:** Solve graph → feed result as facts to placement → feed to content
2. **Unified:** Load all .lp files, solve once for globally consistent solution

Mode 2 is more powerful but slower. The toolkit supports both for experimentation.

## Test Harness Per Layer

Each layer's test script:
- Runs the layer in isolation with sample inputs
- Prints solve time
- Renders output (networkx graph, ASCII dungeon, item list)
- Compares against equivalent procedural Python for expressiveness comparison

## Success Criteria

After building this toolkit, we should be able to answer:
1. Which layers benefit most from ASP's declarative style?
2. Where does clingo's performance become a bottleneck?
3. Is the expressiveness gain worth the learning curve and tooling overhead?
