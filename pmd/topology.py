#!/usr/bin/env python3
"""Stage 1: Generate room topology using ASP/Clingo."""

import sys
import random
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

PMD_DIR = Path(__file__).parent


@dataclass
class Room:
    """Room from ASP solver with grid position."""
    id: int
    gx: int
    gy: int
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


@dataclass
class Topology:
    """Room topology from ASP solver."""
    rooms: Dict[int, Room]
    connections: List[Tuple[int, int]]
    item_types: Dict[int, str]
    enemy_types: Dict[int, str]
    trap_types: Dict[int, str]
    grid_size: int


def generate_topology(num_rooms: int = 7, grid_size: int = 4) -> Topology:
    """Generate room topology using Clingo ASP solver."""
    seed = random.randint(1, 100000)

    cmd = [
        sys.executable, "-m", "clingo",
        str(PMD_DIR / "floor_clingcon_full.lp"),
        "--models=1",
        f"-c num_rooms={num_rooms}",
        f"-c grid_size={grid_size}",
        f"--seed={seed}",
        "--sign-def=rnd",
        "--rand-freq=0.5",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr

    if "SATISFIABLE" not in output and "OPTIMUM FOUND" not in output:
        return None

    return _parse_output(output, grid_size)


def _parse_output(output: str, grid_size: int) -> Topology:
    """Parse Clingo output into Topology."""
    data = {
        "rooms": {}, "corridors": [], "item_types": {}, "enemy_types": {},
        "trap_types": {}, "room_gx": {}, "room_gy": {}, "room_widths": {}, "room_heights": {},
    }

    answer_match = re.search(r'Answer: \d+[^\n]*\n(.*?)(?:\nOptimization:|SATISFIABLE|$)', output, re.DOTALL)
    if not answer_match:
        answer_match = re.search(r'Answer: \d+[^\n]*\n(.*?)$', output, re.DOTALL)

    if not answer_match:
        return None

    atoms = answer_match.group(1).strip().split()

    patterns = [
        (r'room\((\d+)\)', lambda m: data["rooms"].setdefault(int(m.group(1)), {"id": int(m.group(1))})),
        (r'corridor\((\d+),(\d+)\)', lambda m: data["corridors"].append((int(m.group(1)), int(m.group(2))))),
        (r'is_spawn\((\d+)\)', lambda m: data["rooms"].setdefault(int(m.group(1)), {"id": int(m.group(1))}).update(is_spawn=True)),
        (r'has_stairs\((\d+)\)', lambda m: data["rooms"].setdefault(int(m.group(1)), {"id": int(m.group(1))}).update(is_stairs=True)),
        (r'room_width\((\d+),(\d+)\)', lambda m: data["room_widths"].__setitem__(int(m.group(1)), int(m.group(2)))),
        (r'room_height\((\d+),(\d+)\)', lambda m: data["room_heights"].__setitem__(int(m.group(1)), int(m.group(2)))),
        (r'room_gx\((\d+),(\d+)\)', lambda m: data["room_gx"].__setitem__(int(m.group(1)), int(m.group(2)))),
        (r'room_gy\((\d+),(\d+)\)', lambda m: data["room_gy"].__setitem__(int(m.group(1)), int(m.group(2)))),
        (r'item_in\((\d+),(\d+)\)', lambda m: data["rooms"].setdefault(int(m.group(2)), {"id": int(m.group(2))}).setdefault("items", []).append(int(m.group(1)))),
        (r'item_is\((\d+),(\w+)\)', lambda m: data["item_types"].__setitem__(int(m.group(1)), m.group(2))),
        (r'enemy_in\((\d+),(\d+)\)', lambda m: data["rooms"].setdefault(int(m.group(2)), {"id": int(m.group(2))}).setdefault("enemies", []).append(int(m.group(1)))),
        (r'enemy_is\((\d+),(\w+)\)', lambda m: data["enemy_types"].__setitem__(int(m.group(1)), m.group(2))),
        (r'trap_in\((\d+),(\d+)\)', lambda m: data["rooms"].setdefault(int(m.group(2)), {"id": int(m.group(2))}).setdefault("traps", []).append(int(m.group(1)))),
        (r'trap_is\((\d+),(\w+)\)', lambda m: data["trap_types"].__setitem__(int(m.group(1)), m.group(2))),
    ]

    for atom in atoms:
        for pattern, handler in patterns:
            m = re.match(pattern, atom)
            if m:
                handler(m)
                break

    rooms = {}
    for rid, room_data in data["rooms"].items():
        rooms[rid] = Room(
            id=rid,
            gx=data["room_gx"].get(rid, 0),
            gy=data["room_gy"].get(rid, 0),
            width=data["room_widths"].get(rid, 6),
            height=data["room_heights"].get(rid, 6),
            is_spawn=room_data.get("is_spawn", False),
            is_stairs=room_data.get("is_stairs", False),
            items=room_data.get("items", []),
            enemies=room_data.get("enemies", []),
            traps=room_data.get("traps", []),
        )

    return Topology(
        rooms=rooms,
        connections=data["corridors"],
        item_types=data["item_types"],
        enemy_types=data["enemy_types"],
        trap_types=data["trap_types"],
        grid_size=grid_size,
    )
