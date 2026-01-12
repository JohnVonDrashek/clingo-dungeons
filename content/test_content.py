#!/usr/bin/env python3
"""Test and visualize content placement."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runner import solve, facts_from_solution

CONTENT_DIR = Path(__file__).parent
GRAPH_DIR = CONTENT_DIR.parent / "graph"


def generate_content(
    num_rooms: int = 8,
    num_items: int = 5,
    num_enemies: int = 6,
    num_keys: int = 2,
    num_solutions: int = 1,
) -> tuple[dict | None, dict | None, float, float]:
    """
    Generate graph then place content.

    Returns: (graph_solution, content_solution, graph_time_ms, content_time_ms)
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

    # Step 2: Place content using graph
    # Note: edge/2 is derived in topology.lp but not shown, so we generate it here
    graph_facts = facts_from_solution(
        graph, ["room", "connects", "room_type", "min_dist"]
    )
    # Add edge facts from connects (symmetric)
    for r1, r2 in graph.get("connects", []):
        graph_facts += f"\nedge({r1},{r2}). edge({r2},{r1})."

    start = time.perf_counter()
    content_solutions = solve(
        [
            CONTENT_DIR / "items.lp",
            CONTENT_DIR / "enemies.lp",
            CONTENT_DIR / "keys_locks.lp",
        ],
        extra_facts=graph_facts,
        constants={
            "num_rooms": num_rooms,
            "num_items": num_items,
            "num_enemies": num_enemies,
            "num_keys": num_keys,
        },
        num_solutions=num_solutions,
    )
    content_time = (time.perf_counter() - start) * 1000

    if not content_solutions:
        return graph, None, graph_time, content_time

    # Merge for display
    content = content_solutions[0]
    content["room"] = graph.get("room", [])
    content["room_type"] = graph.get("room_type", [])
    content["connects"] = graph.get("connects", [])
    content["min_dist"] = graph.get("min_dist", [])

    return graph, content, graph_time, content_time


def visualize_content(graph: dict, content: dict) -> str:
    """Visualize content placement."""
    lines = []

    rooms = sorted(r[0] for r in graph.get("room", []))
    room_types = {r: t for r, t in graph.get("room_type", [])}
    distances = {r: d for r, d in graph.get("min_dist", [])}
    connects = graph.get("connects", [])

    # Content data
    items_in = {}
    for item, room in content.get("item_in", []):
        items_in.setdefault(room, []).append(item)
    item_types = {i: t for i, t in content.get("item_is", [])}

    enemies_in = {}
    for enemy, room in content.get("enemy_in", []):
        enemies_in.setdefault(room, []).append(enemy)
    enemy_types = {e: t for e, t in content.get("enemy_is", [])}
    enemy_diff = {e: d for e, d in content.get("enemy_difficulty", [])}
    room_tiers = {r: t for r, t in content.get("room_tier", [])}

    keys_in = {r: c for c, r in content.get("key_in", [])}
    locked_doors = [(r1, r2, c) for r1, r2, c in content.get("locked_door_norm", [])]

    lines.append("=== Dungeon Content ===")
    lines.append("")

    for r in rooms:
        t = room_types.get(r, "normal")
        d = distances.get(r, "?")
        tier = room_tiers.get(r, "?")

        type_marker = {"spawn": "[SPAWN]", "boss": "[BOSS]", "shop": "[SHOP]",
                       "treasure": "[TREASURE]", "normal": ""}

        lines.append(f"Room {r} {type_marker.get(t, '')} (dist={d}, tier={tier})")

        # Items
        room_items = items_in.get(r, [])
        if room_items:
            item_strs = [f"{item_types.get(i, '?')}" for i in room_items]
            lines.append(f"  Items: {', '.join(item_strs)}")

        # Enemies
        room_enemies = enemies_in.get(r, [])
        if room_enemies:
            enemy_strs = [f"{enemy_types.get(e, '?')}(d={enemy_diff.get(e, '?')})"
                         for e in room_enemies]
            lines.append(f"  Enemies: {', '.join(enemy_strs)}")

        # Keys
        if r in keys_in:
            lines.append(f"  Key: {keys_in[r]}")

        lines.append("")

    # Locked doors
    if locked_doors:
        lines.append("Locked Doors:")
        for r1, r2, color in locked_doors:
            lines.append(f"  {r1} <--[{color}]--> {r2}")
        lines.append("")

    # Connections
    lines.append("Connections:")
    for r1, r2 in sorted(connects):
        lock_marker = ""
        for lr1, lr2, c in locked_doors:
            if (lr1, lr2) == (r1, r2) or (lr1, lr2) == (r2, r1):
                lock_marker = f" [{c} lock]"
        lines.append(f"  {r1} -- {r2}{lock_marker}")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test content placement")
    parser.add_argument("-n", "--num-rooms", type=int, default=8, help="Number of rooms")
    parser.add_argument("--items", type=int, default=5, help="Number of items")
    parser.add_argument("--enemies", type=int, default=6, help="Number of enemies")
    parser.add_argument("--keys", type=int, default=2, help="Number of keys")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    args = parser.parse_args()

    if args.benchmark:
        print("=== Content Benchmark ===")
        print(f"{'Rooms':>6} | {'Graph (ms)':>10} | {'Content (ms)':>12} | {'Success'}")
        print("-" * 55)

        for num_rooms in [5, 8, 10, 12, 15]:
            graph, content, gt, ct = generate_content(
                num_rooms=num_rooms,
                num_items=num_rooms,
                num_enemies=num_rooms,
                num_keys=min(2, num_rooms // 4),
            )
            success = "Yes" if content else "No"
            print(f"{num_rooms:>6} | {gt:>10.1f} | {ct:>12.1f} | {success}")
        return

    print(f"Generating content for {args.num_rooms} rooms")
    print(f"Items: {args.items}, Enemies: {args.enemies}, Keys: {args.keys}")
    print()

    graph, content, graph_time, content_time = generate_content(
        num_rooms=args.num_rooms,
        num_items=args.items,
        num_enemies=args.enemies,
        num_keys=args.keys,
    )

    print(f"Graph time: {graph_time:.1f}ms")
    print(f"Content time: {content_time:.1f}ms")
    print()

    if not graph:
        print("Failed to generate graph!")
        return

    if not content:
        print("Failed to place content!")
        print("Graph was valid but content constraints unsatisfiable.")
        return

    print(visualize_content(graph, content))


if __name__ == "__main__":
    main()
