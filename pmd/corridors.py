#!/usr/bin/env python3
"""Stage 3: Calculate corridor paths using Bresenham."""

from typing import List, Dict, Tuple

from placement import PlacedRoom


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


def calculate_corridors(placed_rooms: Dict[int, PlacedRoom],
                        connections: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    """Calculate corridor paths between connected rooms."""
    corridor_paths = []
    for r1_id, r2_id in connections:
        if r1_id not in placed_rooms or r2_id not in placed_rooms:
            continue
        r1, r2 = placed_rooms[r1_id], placed_rooms[r2_id]
        start = (r1.x + r1.width // 2, r1.y + r1.height // 2)
        end = (r2.x + r2.width // 2, r2.y + r2.height // 2)
        corridor_paths.append(bresenham_path(start, end))
    return corridor_paths
