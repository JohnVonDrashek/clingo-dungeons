#!/usr/bin/env python3
"""
Generate PMD dungeon using clingo for room topology and grid placement.
Uses ASP for room connections and coarse grid positioning.
"""

import sys
import random
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

import networkx as nx

# Directory containing this script and the LP files
PMD_DIR = Path(__file__).parent


@dataclass
class Room:
    """Room from ASP solver with grid position."""
    id: int
    gx: int  # grid x position (0 to grid_size-1)
    gy: int  # grid y position (0 to grid_size-1)
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


def place_rooms(rooms: Dict[int, Room], corridors: List[Tuple[int, int]],
                min_gap: int = 2) -> Dict[int, PlacedRoom]:
    """Place rooms using force-directed layout, enforcing minimum gap."""
    G = nx.Graph()
    for rid in rooms:
        G.add_node(rid)
    for r1, r2 in corridors:
        G.add_edge(r1, r2)

    pos = nx.spring_layout(G, k=2.0, iterations=100, seed=None)

    # Scale positions to tile coordinates
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    total_width = sum(r.width for r in rooms.values())
    total_height = sum(r.height for r in rooms.values())
    avg_size = (total_width + total_height) / (2 * len(rooms))
    scale = (avg_size + min_gap) * 2.5

    placed = {}
    for rid, room in rooms.items():
        px, py = pos[rid]
        x = int((px - min(xs)) * scale)
        y = int((py - min(ys)) * scale)
        placed[rid] = PlacedRoom(
            id=rid, x=x, y=y, width=room.width, height=room.height,
            is_spawn=room.is_spawn, is_stairs=room.is_stairs,
            items=room.items, enemies=room.enemies, traps=room.traps,
        )

    # Push apart overlapping rooms
    room_ids = list(placed.keys())
    for _ in range(50):
        moved = False
        for i, rid1 in enumerate(room_ids):
            for rid2 in room_ids[i+1:]:
                if _push_apart(placed[rid1], placed[rid2], min_gap):
                    moved = True
        if not moved:
            break

    # Normalize so min x,y is 0
    min_x = min(r.x for r in placed.values())
    min_y = min(r.y for r in placed.values())
    for room in placed.values():
        room.x -= min_x
        room.y -= min_y

    return placed


def _push_apart(r1: PlacedRoom, r2: PlacedRoom, min_gap: int) -> bool:
    """Push rooms apart if overlapping. Returns True if moved."""
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


def parse_clingo_output(output: str) -> dict:
    """Parse clingo output for room topology and grid positions."""
    data = {
        "rooms": {},
        "corridors": [],
        "item_types": {},
        "enemy_types": {},
        "trap_types": {},
        "room_gx": {},
        "room_gy": {},
        "room_widths": {},
        "room_heights": {},
    }

    # Parse atoms from Answer line (format: "Answer: N (Time: ...)\natoms...")
    # or "Answer: N\natoms..."
    answer_match = re.search(r'Answer: \d+[^\n]*\n(.*?)(?:\nOptimization:|SATISFIABLE|$)', output, re.DOTALL)
    if not answer_match:
        answer_match = re.search(r'Answer: \d+[^\n]*\n(.*?)$', output, re.DOTALL)

    if answer_match:
        atoms_str = answer_match.group(1).strip()
        atoms = atoms_str.split()

        for atom in atoms:
            # Parse room(N)
            m = re.match(r'room\((\d+)\)', atom)
            if m:
                rid = int(m.group(1))
                if rid not in data["rooms"]:
                    data["rooms"][rid] = {"id": rid}
                continue

            # Parse corridor(R1,R2)
            m = re.match(r'corridor\((\d+),(\d+)\)', atom)
            if m:
                data["corridors"].append((int(m.group(1)), int(m.group(2))))
                continue

            # Parse is_spawn(R)
            m = re.match(r'is_spawn\((\d+)\)', atom)
            if m:
                rid = int(m.group(1))
                if rid not in data["rooms"]:
                    data["rooms"][rid] = {"id": rid}
                data["rooms"][rid]["is_spawn"] = True
                continue

            # Parse has_stairs(R)
            m = re.match(r'has_stairs\((\d+)\)', atom)
            if m:
                rid = int(m.group(1))
                if rid not in data["rooms"]:
                    data["rooms"][rid] = {"id": rid}
                data["rooms"][rid]["is_stairs"] = True
                continue

            # Parse room_width(R, W)
            m = re.match(r'room_width\((\d+),(\d+)\)', atom)
            if m:
                data["room_widths"][int(m.group(1))] = int(m.group(2))
                continue

            # Parse room_height(R, H)
            m = re.match(r'room_height\((\d+),(\d+)\)', atom)
            if m:
                data["room_heights"][int(m.group(1))] = int(m.group(2))
                continue

            # Parse room_gx(R, X)
            m = re.match(r'room_gx\((\d+),(\d+)\)', atom)
            if m:
                data["room_gx"][int(m.group(1))] = int(m.group(2))
                continue

            # Parse room_gy(R, Y)
            m = re.match(r'room_gy\((\d+),(\d+)\)', atom)
            if m:
                data["room_gy"][int(m.group(1))] = int(m.group(2))
                continue

            # Parse item_in(I, R)
            m = re.match(r'item_in\((\d+),(\d+)\)', atom)
            if m:
                item_id, rid = int(m.group(1)), int(m.group(2))
                if rid not in data["rooms"]:
                    data["rooms"][rid] = {"id": rid}
                if "items" not in data["rooms"][rid]:
                    data["rooms"][rid]["items"] = []
                data["rooms"][rid]["items"].append(item_id)
                continue

            # Parse item_is(I, T)
            m = re.match(r'item_is\((\d+),(\w+)\)', atom)
            if m:
                data["item_types"][int(m.group(1))] = m.group(2)
                continue

            # Parse enemy_in(E, R)
            m = re.match(r'enemy_in\((\d+),(\d+)\)', atom)
            if m:
                enemy_id, rid = int(m.group(1)), int(m.group(2))
                if rid not in data["rooms"]:
                    data["rooms"][rid] = {"id": rid}
                if "enemies" not in data["rooms"][rid]:
                    data["rooms"][rid]["enemies"] = []
                data["rooms"][rid]["enemies"].append(enemy_id)
                continue

            # Parse enemy_is(E, T)
            m = re.match(r'enemy_is\((\d+),(\w+)\)', atom)
            if m:
                data["enemy_types"][int(m.group(1))] = m.group(2)
                continue

            # Parse trap_in(T, R)
            m = re.match(r'trap_in\((\d+),(\d+)\)', atom)
            if m:
                trap_id, rid = int(m.group(1)), int(m.group(2))
                if rid not in data["rooms"]:
                    data["rooms"][rid] = {"id": rid}
                if "traps" not in data["rooms"][rid]:
                    data["rooms"][rid]["traps"] = []
                data["rooms"][rid]["traps"].append(trap_id)
                continue

            # Parse trap_is(T, Ty)
            m = re.match(r'trap_is\((\d+),(\w+)\)', atom)
            if m:
                data["trap_types"][int(m.group(1))] = m.group(2)
                continue

    return data


def generate_clingcon_floor(num_rooms=7, grid_size=4, **kwargs):
    """Generate a PMD floor using clingo for room topology and grid placement."""
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
        print("Error: No solution found")
        print(output)
        return None

    raw_data = parse_clingo_output(output)

    # Convert to Room objects
    rooms = {}
    for rid, room_data in raw_data["rooms"].items():
        width = raw_data["room_widths"].get(rid, 6)
        height = raw_data["room_heights"].get(rid, 6)
        gx = raw_data["room_gx"].get(rid, 0)
        gy = raw_data["room_gy"].get(rid, 0)

        rooms[rid] = Room(
            id=rid,
            gx=gx,
            gy=gy,
            width=width,
            height=height,
            is_spawn=room_data.get("is_spawn", False),
            is_stairs=room_data.get("is_stairs", False),
            items=room_data.get("items", []),
            enemies=room_data.get("enemies", []),
            traps=room_data.get("traps", []),
        )

    return {
        "rooms": rooms,
        "corridors": raw_data["corridors"],
        "item_types": raw_data["item_types"],
        "enemy_types": raw_data["enemy_types"],
        "trap_types": raw_data["trap_types"],
        "grid_size": grid_size,
    }


def print_summary(data: dict):
    """Print summary of the generated floor."""
    rooms = data["rooms"]
    print("=" * 60)
    print("PMD FLOOR SUMMARY (Grid Topology)")
    print("=" * 60)
    print()
    print(f"Grid size: {data['grid_size']}x{data['grid_size']}")
    print(f"Rooms: {len(rooms)}")
    print(f"Corridors: {len(data['corridors'])}")

    spawn = [r for r in rooms.values() if r.is_spawn]
    stairs = [r for r in rooms.values() if r.is_stairs]
    if spawn:
        print(f"Spawn: Room {spawn[0].id} @ grid ({spawn[0].gx},{spawn[0].gy}) {spawn[0].width}x{spawn[0].height}")
    if stairs:
        print(f"Stairs: Room {stairs[0].id} @ grid ({stairs[0].gx},{stairs[0].gy}) {stairs[0].width}x{stairs[0].height}")
    print()

    print("Room Positions:")
    for rid in sorted(rooms.keys()):
        room = rooms[rid]
        parts = [f"  Room {rid}: grid ({room.gx},{room.gy}) {room.width}x{room.height}"]
        if room.is_spawn:
            parts.append("SPAWN")
        if room.is_stairs:
            parts.append("STAIRS")
        print(" ".join(parts))

        for item_id in room.items:
            item_type = data["item_types"].get(item_id, "?")
            print(f"    - Item: {item_type}")
        for enemy_id in room.enemies:
            enemy_type = data["enemy_types"].get(enemy_id, "?")
            print(f"    - Enemy: {enemy_type}")
        for trap_id in room.traps:
            trap_type = data["trap_types"].get(trap_id, "?")
            print(f"    - Trap: {trap_type}")
    print()


def main():
    num_rooms = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    grid_size = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    print(f"Generating {num_rooms}-room floor on {grid_size}x{grid_size} grid...")
    print()

    data = generate_clingcon_floor(num_rooms, grid_size)
    if data is None:
        sys.exit(1)

    print_summary(data)

    print("Connections:")
    for r1, r2 in data["corridors"]:
        room1 = data["rooms"][r1]
        room2 = data["rooms"][r2]
        print(f"  Room {r1} ({room1.gx},{room1.gy}) <-> Room {r2} ({room2.gx},{room2.gy})")


if __name__ == "__main__":
    main()
