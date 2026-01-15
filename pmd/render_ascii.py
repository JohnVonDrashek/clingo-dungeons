#!/usr/bin/env python3
"""Render dungeon as ASCII grid."""

import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set

sys.path.insert(0, str(Path(__file__).parent))
from generate_clingcon import generate_clingcon_floor, place_rooms, PlacedRoom


def bresenham_path(start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Bresenham's line algorithm - cardinal-only steps."""
    x1, y1 = start
    x2, y2 = end
    path = [(x1, y1)]

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    err = dx - dy
    x, y = x1, y1

    while x != x2 or y != y2:
        e2 = 2 * err
        if e2 > -dy and (e2 < dx and dx > dy or e2 >= dx):
            err -= dy
            x += sx
        elif e2 < dx:
            err += dx
            y += sy
        elif e2 > -dy:
            err -= dy
            x += sx
        path.append((x, y))

    return path


def render_ascii(placed_rooms: Dict[int, PlacedRoom],
                 corridors: List[Tuple[int, int]]) -> str:
    """Render placed rooms and corridors to ASCII grid."""
    max_x = max(r.x + r.width for r in placed_rooms.values()) + 2
    max_y = max(r.y + r.height for r in placed_rooms.values()) + 2

    grid = [[' ' for _ in range(max_x)] for _ in range(max_y)]
    room_tiles: Set[Tuple[int, int]] = set()

    # Draw rooms
    for room in placed_rooms.values():
        for rx in range(room.x, room.x + room.width):
            for ry in range(room.y, room.y + room.height):
                if 0 <= rx < max_x and 0 <= ry < max_y:
                    grid[ry][rx] = '.'
                    room_tiles.add((rx, ry))

        cx, cy = room.x + room.width // 2, room.y + room.height // 2
        if 0 <= cx < max_x and 0 <= cy < max_y:
            if room.is_spawn:
                grid[cy][cx] = 'S'
            elif room.is_stairs:
                grid[cy][cx] = '>'

    # Draw corridors
    for r1_id, r2_id in corridors:
        if r1_id not in placed_rooms or r2_id not in placed_rooms:
            continue

        r1, r2 = placed_rooms[r1_id], placed_rooms[r2_id]
        start = (r1.x + r1.width // 2, r1.y + r1.height // 2)
        end = (r2.x + r2.width // 2, r2.y + r2.height // 2)

        for px, py in bresenham_path(start, end):
            if 0 <= px < max_x and 0 <= py < max_y:
                if grid[py][px] == ' ':
                    grid[py][px] = ','

    return '\n'.join(''.join(row) for row in grid)


def generate_ascii_dungeon(num_rooms: int = 7, min_gap: int = 2) -> Tuple[str, dict]:
    """Generate a complete ASCII dungeon."""
    data = generate_clingcon_floor(num_rooms)
    if data is None:
        return None, None

    placed = place_rooms(data["rooms"], data["corridors"], min_gap=min_gap)
    ascii_grid = render_ascii(placed, data["corridors"])

    return ascii_grid, {
        "placed_rooms": placed,
        "corridors": data["corridors"],
        "item_types": data["item_types"],
        "enemy_types": data["enemy_types"],
        "trap_types": data["trap_types"],
    }


def main():
    num_rooms = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Generating {num_rooms}-room ASCII dungeon...")

    ascii_grid, data = generate_ascii_dungeon(num_rooms)

    if ascii_grid is None:
        print("Failed to generate dungeon")
        sys.exit(1)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(ascii_grid)
        print(f"Saved to {output_file}")
    else:
        print()
        print(ascii_grid)
        print()
        print("Legend: . = room floor, , = corridor, S = spawn, > = stairs")


if __name__ == "__main__":
    main()
