#!/usr/bin/env python3
"""Stage 2: Place rooms using force-directed physics."""

from typing import List, Dict, Tuple
from dataclasses import dataclass

import networkx as nx

from topology import Room, Topology


@dataclass
class PlacedRoom:
    """Room with pixel position after physics simulation."""
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
    """Place rooms using force-directed layout."""
    G = nx.Graph()
    for rid in topology.rooms:
        G.add_node(rid)
    for r1, r2 in topology.connections:
        G.add_edge(r1, r2)

    pos = nx.spring_layout(G, k=2.0, iterations=100, seed=None)

    # Scale to tile coordinates
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    total_size = sum(r.width + r.height for r in topology.rooms.values())
    avg_size = total_size / (2 * len(topology.rooms))
    scale = (avg_size + min_gap) * 2.5

    placed = {}
    for rid, room in topology.rooms.items():
        px, py = pos[rid]
        x = int((px - min(xs)) * scale)
        y = int((py - min(ys)) * scale)
        placed[rid] = PlacedRoom(
            id=rid, x=x, y=y, width=room.width, height=room.height,
            is_spawn=room.is_spawn, is_stairs=room.is_stairs,
            items=room.items, enemies=room.enemies, traps=room.traps,
        )

    # Push apart overlapping rooms
    _enforce_gaps(placed, min_gap)

    # Normalize to origin
    min_x = min(r.x for r in placed.values())
    min_y = min(r.y for r in placed.values())
    for room in placed.values():
        room.x -= min_x
        room.y -= min_y

    return placed


def _enforce_gaps(placed: Dict[int, PlacedRoom], min_gap: int):
    """Push rooms apart until minimum gap is achieved."""
    room_ids = list(placed.keys())
    for _ in range(50):
        moved = False
        for i, rid1 in enumerate(room_ids):
            for rid2 in room_ids[i+1:]:
                if _push_apart(placed[rid1], placed[rid2], min_gap):
                    moved = True
        if not moved:
            break


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
