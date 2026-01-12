#!/usr/bin/env python3
"""Test and visualize dungeon graph generation."""

import sys
import time
from pathlib import Path

# Add parent to path for runner import
sys.path.insert(0, str(Path(__file__).parent.parent))

from runner import solve

GRAPH_DIR = Path(__file__).parent


def generate_graph(
    num_rooms: int = 8,
    min_boss_distance: int = 3,
    allow_cycles: bool = True,
    num_solutions: int = 1,
) -> list[dict]:
    """Generate dungeon graph(s) with given parameters."""
    return solve(
        [GRAPH_DIR / "topology.lp", GRAPH_DIR / "critical_path.lp"],
        constants={
            "num_rooms": num_rooms,
            "min_boss_distance": min_boss_distance,
            "allow_cycles": 1 if allow_cycles else 0,
        },
        num_solutions=num_solutions,
    )


def visualize_ascii(solution: dict) -> str:
    """Simple ASCII visualization of graph structure."""
    lines = []

    # Get room info
    rooms = sorted(r[0] for r in solution.get("room", []))
    room_types = {r: t for r, t in solution.get("room_type", [])}
    connections = solution.get("connects", [])
    distances = {r: d for r, d in solution.get("min_dist", [])}
    critical = set(r[0] for r in solution.get("on_critical_path", []))

    # Type symbols
    type_symbol = {"spawn": "@", "boss": "B", "shop": "$", "treasure": "T", "normal": "."}

    lines.append("=== Dungeon Graph ===")
    lines.append("")

    # Room list
    lines.append("Rooms:")
    for r in rooms:
        t = room_types.get(r, "normal")
        d = distances.get(r, "?")
        crit = "*" if r in critical else " "
        lines.append(f"  [{type_symbol[t]}] Room {r}: {t}, dist={d} {crit}")

    lines.append("")
    lines.append("Connections:")
    for r1, r2 in sorted(connections):
        lines.append(f"  {r1} -- {r2}")

    lines.append("")
    lines.append("Legend: @ spawn, B boss, $ shop, T treasure, . normal")
    lines.append("        * = on critical path")

    return "\n".join(lines)


def visualize_networkx(solution: dict) -> None:
    """Visualize using networkx (prints adjacency if matplotlib unavailable)."""
    try:
        import networkx as nx
    except ImportError:
        print("networkx not available")
        return

    G = nx.Graph()

    rooms = [r[0] for r in solution.get("room", [])]
    room_types = {r: t for r, t in solution.get("room_type", [])}
    connections = solution.get("connects", [])
    critical = set(r[0] for r in solution.get("on_critical_path", []))

    for r in rooms:
        G.add_node(r, type=room_types.get(r, "normal"))

    for r1, r2 in connections:
        G.add_edge(r1, r2)

    print("\nNetworkX adjacency:")
    for node in sorted(G.nodes()):
        neighbors = sorted(G.neighbors(node))
        t = room_types.get(node, "?")
        crit = "*" if node in critical else ""
        print(f"  {node} ({t}{crit}): {neighbors}")


def benchmark(num_rooms_list: list[int], trials: int = 3) -> None:
    """Benchmark solve times for different dungeon sizes."""
    print("\n=== Benchmark ===")
    print(f"{'Rooms':>6} | {'Time (ms)':>10} | {'Solutions'}")
    print("-" * 35)

    for num_rooms in num_rooms_list:
        times = []
        solutions_found = 0
        for _ in range(trials):
            start = time.perf_counter()
            solutions = generate_graph(num_rooms=num_rooms, num_solutions=1)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            solutions_found = len(solutions)

        avg_time = sum(times) / len(times)
        print(f"{num_rooms:>6} | {avg_time:>10.2f} | {solutions_found}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test dungeon graph generation")
    parser.add_argument("-n", "--num-rooms", type=int, default=8, help="Number of rooms")
    parser.add_argument("-d", "--min-boss-dist", type=int, default=3, help="Min boss distance")
    parser.add_argument("--no-cycles", action="store_true", help="Generate tree only")
    parser.add_argument("-s", "--solutions", type=int, default=1, help="Number of solutions")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    args = parser.parse_args()

    if args.benchmark:
        benchmark([5, 8, 10, 12, 15, 20])
        return

    print(f"Generating dungeon graph: {args.num_rooms} rooms, min_boss_dist={args.min_boss_dist}")
    print(f"Cycles allowed: {not args.no_cycles}")
    print()

    start = time.perf_counter()
    solutions = generate_graph(
        num_rooms=args.num_rooms,
        min_boss_distance=args.min_boss_dist,
        allow_cycles=not args.no_cycles,
        num_solutions=args.solutions,
    )
    elapsed = (time.perf_counter() - start) * 1000

    print(f"Solve time: {elapsed:.2f}ms")
    print(f"Solutions found: {len(solutions)}")

    if not solutions:
        print("No valid dungeon found!")
        return

    for i, sol in enumerate(solutions):
        if len(solutions) > 1:
            print(f"\n--- Solution {i+1} ---")
        print()
        print(visualize_ascii(sol))
        visualize_networkx(sol)


if __name__ == "__main__":
    main()
