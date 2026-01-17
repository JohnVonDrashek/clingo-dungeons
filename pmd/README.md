# pmd

Core dungeon generation pipeline.

## Files

| File | Purpose |
|------|---------|
| `topology.py` | Generate room graph with Clingo ASP |
| `placement.py` | Position rooms (force-directed layout) |
| `corridors.py` | Route corridors (Bresenham algorithm) |
| `render_ascii.py` | Output ASCII text grid |
| `visualize_graph.py` | Output PNG graph visualization |
| `dungeon.py` | Shared data structures |

## ASP Rules

| File | Purpose |
|------|---------|
| `floor_clingcon_full.lp` | Main dungeon constraints |
| `placement.lp` | Room placement rules |

## Configuration

Edit constants in `floor_clingcon_full.lp`:

```prolog
#const num_rooms = 7.
#const num_items = 4.
#const num_enemies = 5.
#const num_traps = 2.
#const min_room_size = 4.
#const max_room_size = 8.
```
