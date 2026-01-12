#!/usr/bin/env python3
"""Test and visualize room placement."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runner import solve, facts_from_solution

PLACEMENT_DIR = Path(__file__).parent
GRAPH_DIR = PLACEMENT_DIR.parent / "graph"


def generate_placement(
    num_rooms: int = 5,
    grid_size: int = 30,
    min_room_size: int = 5,
    max_room_size: int = 8,
    num_solutions: int = 1,
) -> tuple[dict | None, dict | None, float, float]:
    """
    Generate graph then place rooms.

    Returns: (graph_solution, placement_solution, graph_time_ms, placement_time_ms)
    """
    # Step 1: Generate graph
    start = time.perf_counter()
    graph_solutions = solve(
        [GRAPH_DIR / "topology.lp", GRAPH_DIR / "critical_path.lp"],
        constants={
            "num_rooms": num_rooms,
            "min_boss_distance": max(2, num_rooms // 3),
            "allow_cycles": 1,
        },
        num_solutions=1,
    )
    graph_time = (time.perf_counter() - start) * 1000

    if not graph_solutions:
        return None, None, graph_time, 0

    graph = graph_solutions[0]

    # Step 2: Place rooms using graph as input
    graph_facts = facts_from_solution(graph, ["room", "connects", "room_type"])

    # Use coarse grid for reasonable performance
    grid_cells = max(2, int(grid_size / 12))

    start = time.perf_counter()
    placement_solutions = solve(
        [
            PLACEMENT_DIR / "rooms_coarse.lp",
            PLACEMENT_DIR / "corridors.lp",
        ],
        extra_facts=graph_facts,
        constants={
            "grid_cells_x": grid_cells,
            "grid_cells_y": grid_cells,
            "cell_size": 12,
            "min_room_size": min_room_size,
            "max_room_size": max_room_size,
        },
        num_solutions=num_solutions,
    )
    placement_time = (time.perf_counter() - start) * 1000

    if not placement_solutions:
        return graph, None, graph_time, placement_time

    # Merge graph info into placement for rendering
    placement = placement_solutions[0]
    placement["room_type"] = graph.get("room_type", [])
    placement["connects"] = graph.get("connects", [])

    return graph, placement, graph_time, placement_time


def render_ascii(placement: dict, grid_size: int = 30) -> str:
    """Render placement as ASCII grid."""
    # Initialize grid
    grid = [[" " for _ in range(grid_size)] for _ in range(grid_size)]

    # Get room data
    room_x = {r: x for r, x in placement.get("room_x", [])}
    room_y = {r: y for r, y in placement.get("room_y", [])}
    room_w = {r: w for r, w in placement.get("room_w", [])}
    room_h = {r: h for r, h in placement.get("room_h", [])}
    room_types = {r: t for r, t in placement.get("room_type", [])}

    # Type symbols
    floor_char = {
        "spawn": "@",
        "boss": "B",
        "shop": "$",
        "treasure": "T",
        "normal": ".",
    }

    # Draw rooms
    for r in room_x.keys():
        x, y = room_x[r], room_y[r]
        w, h = room_w[r], room_h[r]
        t = room_types.get(r, "normal")
        char = floor_char.get(t, ".")

        for dy in range(h):
            for dx in range(w):
                px, py = x + dx, y + dy
                if 0 <= px < grid_size and 0 <= py < grid_size:
                    # Walls on perimeter
                    if dx == 0 or dx == w - 1 or dy == 0 or dy == h - 1:
                        grid[py][px] = "#"
                    else:
                        grid[py][px] = char

    # Draw corridors
    for cx, cy in placement.get("corridor_tile", []):
        if 0 <= cx < grid_size and 0 <= cy < grid_size:
            if grid[cy][cx] == " ":
                grid[cy][cx] = ","
            elif grid[cy][cx] == "#":
                grid[cy][cx] = "+"  # Door

    # Convert to string
    lines = ["".join(row) for row in grid]
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test room placement")
    parser.add_argument("-n", "--num-rooms", type=int, default=4, help="Number of rooms")
    parser.add_argument("-g", "--grid-size", type=int, default=30, help="Grid size")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    args = parser.parse_args()

    if args.benchmark:
        print("=== Placement Benchmark ===")
        print(f"{'Rooms':>6} | {'Graph (ms)':>10} | {'Place (ms)':>10} | {'Success'}")
        print("-" * 50)

        for num_rooms in [3, 4, 5, 6, 8]:
            # Grid needs at least as many cells as rooms
            grid_size = max(36, num_rooms * 12)
            graph, placement, gt, pt = generate_placement(
                num_rooms=num_rooms, grid_size=grid_size
            )
            success = "Yes" if placement else "No"
            print(f"{num_rooms:>6} | {gt:>10.1f} | {pt:>10.1f} | {success}")
        return

    print(f"Generating {args.num_rooms} rooms on {args.grid_size}x{args.grid_size} grid")
    print()

    graph, placement, graph_time, placement_time = generate_placement(
        num_rooms=args.num_rooms, grid_size=args.grid_size
    )

    print(f"Graph time: {graph_time:.1f}ms")
    print(f"Placement time: {placement_time:.1f}ms")
    print()

    if not graph:
        print("Failed to generate graph!")
        return

    if not placement:
        print("Failed to place rooms!")
        print("Graph was valid but placement solver found no solution.")
        print("This might indicate the grid is too small or constraints too tight.")
        return

    print(render_ascii(placement, args.grid_size))
    print()
    print("Legend: # wall, . floor, , corridor, + door")
    print("        @ spawn, B boss, $ shop, T treasure")


if __name__ == "__main__":
    main()
