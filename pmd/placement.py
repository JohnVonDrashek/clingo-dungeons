#!/usr/bin/env python3
"""Stage 2: Place rooms using ASP constraints."""

import sys
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

from topology import Room, Topology

PMD_DIR = Path(__file__).parent


@dataclass
class PlacedRoom:
    """Room with pixel position after placement."""
    id: int
    x: int
    y: int
    width: int
    height: int
    is_spawn: bool = False
    is_stairs: bool = False
    items: List[int] = None
    enemies: List[int] = None
    traps: List[int] = None

    def __post_init__(self):
        self.items = self.items or []
        self.enemies = self.enemies or []
        self.traps = self.traps or []


def place_rooms(topology: Topology, min_gap: int = 2) -> Dict[int, PlacedRoom]:
    """Place rooms using ASP constraint solver."""
    # Calculate bounds - enough space for all rooms plus gaps
    total_size = sum(max(r.width, r.height) + min_gap for r in topology.rooms.values())
    bound = total_size  # Conservative bound

    # Generate facts
    facts = [
        f"#const bound_x = {bound}.",
        f"#const bound_y = {bound}.",
        f"#const min_gap = {min_gap}.",
    ]

    for rid, room in topology.rooms.items():
        facts.append(f"room({rid}).")
        facts.append(f"room_w({rid}, {room.width}).")
        facts.append(f"room_h({rid}, {room.height}).")

    for r1, r2 in topology.connections:
        facts.append(f"connection({r1}, {r2}).")

    # Write facts file
    facts_file = PMD_DIR / "placement_input.lp"
    with open(facts_file, "w") as f:
        f.write("\n".join(facts))

    # Run clingo with timeout
    cmd = [
        sys.executable, "-m", "clingo",
        str(PMD_DIR / "placement.lp"),
        str(facts_file),
        "--opt-mode=optN",
        "--models=1",
        "--time-limit=5",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        facts_file.unlink(missing_ok=True)
        return _fallback_placement(topology, min_gap)

    facts_file.unlink(missing_ok=True)

    # Parse positions
    positions = {}
    for match in re.finditer(r'room_x\((\d+),(\d+)\)', output):
        rid = int(match.group(1))
        positions.setdefault(rid, {})["x"] = int(match.group(2))
    for match in re.finditer(r'room_y\((\d+),(\d+)\)', output):
        rid = int(match.group(1))
        positions.setdefault(rid, {})["y"] = int(match.group(2))

    if not positions:
        return _fallback_placement(topology, min_gap)

    # Build PlacedRoom objects
    placed = {}
    for rid, room in topology.rooms.items():
        if rid in positions:
            placed[rid] = PlacedRoom(
                id=rid,
                x=positions[rid].get("x", 0),
                y=positions[rid].get("y", 0),
                width=room.width,
                height=room.height,
                is_spawn=room.is_spawn,
                is_stairs=room.is_stairs,
                items=room.items,
                enemies=room.enemies,
                traps=room.traps,
            )

    # Normalize to origin
    if placed:
        min_x = min(r.x for r in placed.values())
        min_y = min(r.y for r in placed.values())
        for room in placed.values():
            room.x -= min_x
            room.y -= min_y

    return placed


def _fallback_placement(topology: Topology, min_gap: int) -> Dict[int, PlacedRoom]:
    """Fallback: NetworkX force-directed layout."""
    import networkx as nx

    G = nx.Graph()
    for rid in topology.rooms:
        G.add_node(rid)
    for r1, r2 in topology.connections:
        G.add_edge(r1, r2)

    pos = nx.spring_layout(G, k=2.0, iterations=100)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    total_size = sum(r.width + r.height for r in topology.rooms.values())
    avg_size = total_size / (2 * len(topology.rooms))
    scale = (avg_size + min_gap) * 2.5

    placed = {}
    for rid, room in topology.rooms.items():
        px, py = pos[rid]
        placed[rid] = PlacedRoom(
            id=rid,
            x=int((px - min(xs)) * scale),
            y=int((py - min(ys)) * scale),
            width=room.width,
            height=room.height,
            is_spawn=room.is_spawn,
            is_stairs=room.is_stairs,
            items=room.items,
            enemies=room.enemies,
            traps=room.traps,
        )

    # Enforce gaps
    room_ids = list(placed.keys())
    for _ in range(50):
        moved = False
        for i, rid1 in enumerate(room_ids):
            for rid2 in room_ids[i+1:]:
                if _push_apart(placed[rid1], placed[rid2], min_gap):
                    moved = True
        if not moved:
            break

    min_x = min(r.x for r in placed.values())
    min_y = min(r.y for r in placed.values())
    for room in placed.values():
        room.x -= min_x
        room.y -= min_y

    return placed


def _push_apart(r1: PlacedRoom, r2: PlacedRoom, min_gap: int) -> bool:
    """Push two rooms apart if overlapping."""
    gap_x = max(r2.x - (r1.x + r1.width), r1.x - (r2.x + r2.width))
    gap_y = max(r2.y - (r1.y + r1.height), r1.y - (r2.y + r2.height))

    if gap_x >= min_gap or gap_y >= min_gap:
        return False

    cx1, cy1 = r1.x + r1.width / 2, r1.y + r1.height / 2
    cx2, cy2 = r2.x + r2.width / 2, r2.y + r2.height / 2
    dx, dy = cx2 - cx1, cy2 - cy1

    if abs(dx) > abs(dy):
        needed = (r1.width + r2.width) / 2 + min_gap
        shift = int((needed - abs(dx)) / 2) + 1
        if dx >= 0:
            r1.x -= shift
            r2.x += shift
        else:
            r1.x += shift
            r2.x -= shift
    else:
        needed = (r1.height + r2.height) / 2 + min_gap
        shift = int((needed - abs(dy)) / 2) + 1
        if dy >= 0:
            r1.y -= shift
            r2.y += shift
        else:
            r1.y += shift
            r2.y -= shift

    return True
