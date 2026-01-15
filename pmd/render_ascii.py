#!/usr/bin/env python3
"""Render dungeon as ASCII grid."""

import sys
from pathlib import Path
from typing import Set, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from dungeon import generate_dungeon, Dungeon


def render_ascii(dungeon: Dungeon) -> str:
    """Render a calculated dungeon to ASCII."""
    width = dungeon.width + 2
    height = dungeon.height + 2

    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Draw rooms
    for room in dungeon.rooms.values():
        for rx in range(room.x, room.x + room.width):
            for ry in range(room.y, room.y + room.height):
                if 0 <= rx < width and 0 <= ry < height:
                    grid[ry][rx] = '.'

        cx, cy = room.x + room.width // 2, room.y + room.height // 2
        if 0 <= cx < width and 0 <= cy < height:
            if room.is_spawn:
                grid[cy][cx] = 'S'
            elif room.is_stairs:
                grid[cy][cx] = '>'

    # Draw corridors
    for path in dungeon.corridor_tiles:
        for px, py in path:
            if 0 <= px < width and 0 <= py < height:
                if grid[py][px] == ' ':
                    grid[py][px] = ','

    return '\n'.join(''.join(row) for row in grid)


def main():
    num_rooms = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Generating {num_rooms}-room dungeon...")

    dungeon = generate_dungeon(num_rooms)
    if dungeon is None:
        print("Failed to generate dungeon")
        sys.exit(1)

    ascii_grid = render_ascii(dungeon)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(ascii_grid)
        print(f"Saved to {output_file}")
    else:
        print()
        print(ascii_grid)
        print()
        print("Legend: . = floor, , = corridor, S = spawn, > = stairs")


if __name__ == "__main__":
    main()
