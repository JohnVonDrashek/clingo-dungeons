#!/usr/bin/env python3
"""Dungeon dataclass and pipeline orchestration."""

from typing import List, Dict, Tuple
from dataclasses import dataclass

from topology import generate_topology, Topology
from placement import place_rooms, PlacedRoom
from corridors import calculate_corridors


@dataclass
class Dungeon:
    """Complete calculated dungeon."""
    rooms: Dict[int, PlacedRoom]
    connections: List[Tuple[int, int]]
    corridor_tiles: List[List[Tuple[int, int]]]
    item_types: Dict[int, str]
    enemy_types: Dict[int, str]
    trap_types: Dict[int, str]

    @property
    def width(self) -> int:
        return max(r.x + r.width for r in self.rooms.values()) + 1

    @property
    def height(self) -> int:
        return max(r.y + r.height for r in self.rooms.values()) + 1


def generate_dungeon(num_rooms: int = 7, min_gap: int = 2) -> Dungeon:
    """Generate a complete dungeon through the full pipeline."""
    # Stage 1: Topology from ASP
    topology = generate_topology(num_rooms)
    if topology is None:
        return None

    # Stage 2: Physics placement
    placed = place_rooms(topology, min_gap)

    # Stage 3: Corridor calculation
    corridor_tiles = calculate_corridors(placed, topology.connections)

    return Dungeon(
        rooms=placed,
        connections=topology.connections,
        corridor_tiles=corridor_tiles,
        item_types=topology.item_types,
        enemy_types=topology.enemy_types,
        trap_types=topology.trap_types,
    )
