#!/usr/bin/env python3
"""
Render dungeon as ASCII grid using force-directed room placement and A* corridors.
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Dict, Set

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from generate_clingcon import generate_clingcon_floor, Room


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


def force_directed_placement(rooms: Dict[int, Room], corridors: List[Tuple[int, int]],
                             min_gap: int = 2) -> Dict[int, PlacedRoom]:
    """
    Place rooms using networkx force-directed layout.
    """
    # Build graph for layout
    G = nx.Graph()
    for rid in rooms:
        G.add_node(rid)
    for r1, r2 in corridors:
        G.add_edge(r1, r2)

    # Use networkx spring layout
    pos = nx.spring_layout(G, k=2.0, iterations=100, seed=None)

    # Scale positions to tile coordinates
    # Find bounds of layout
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]

    # Calculate total room sizes to determine scale
    total_width = sum(r.width for r in rooms.values())
    total_height = sum(r.height for r in rooms.values())
    avg_size = (total_width + total_height) / (2 * len(rooms))

    # Scale factor based on room sizes and gap
    scale = (avg_size + min_gap) * 2.5

    # Convert to integer tile positions
    placed = {}
    for rid, room in rooms.items():
        px, py = pos[rid]
        # Scale and shift so all positions are positive
        x = int((px - min(xs)) * scale)
        y = int((py - min(ys)) * scale)

        placed[rid] = PlacedRoom(
            id=rid,
            x=x,
            y=y,
            width=room.width,
            height=room.height,
            is_spawn=room.is_spawn,
            is_stairs=room.is_stairs,
            items=room.items,
            enemies=room.enemies,
            traps=room.traps,
        )

    # Enforce minimum gap between all room pairs
    room_ids = list(placed.keys())
    for _ in range(50):  # Multiple passes to resolve overlaps
        moved = False
        for i, rid1 in enumerate(room_ids):
            for rid2 in room_ids[i+1:]:
                if push_apart(placed[rid1], placed[rid2], min_gap):
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


def push_apart(r1: PlacedRoom, r2: PlacedRoom, min_gap: int) -> bool:
    """Push rooms apart if they overlap or are too close. Returns True if moved."""
    # Check if rooms are too close (including gap)
    gap_x = max(r2.x - (r1.x + r1.width), r1.x - (r2.x + r2.width))
    gap_y = max(r2.y - (r1.y + r1.height), r1.y - (r2.y + r2.height))

    # If either gap is already >= min_gap, they're fine
    if gap_x >= min_gap or gap_y >= min_gap:
        return False

    # Calculate centers
    cx1 = r1.x + r1.width / 2
    cy1 = r1.y + r1.height / 2
    cx2 = r2.x + r2.width / 2
    cy2 = r2.y + r2.height / 2

    dx = cx2 - cx1
    dy = cy2 - cy1

    # Push apart along the shorter axis
    if abs(dx) > abs(dy):
        # Push horizontally
        needed = (r1.width + r2.width) / 2 + min_gap
        if dx >= 0:
            shift = int((needed - dx) / 2) + 1
            r1.x -= shift
            r2.x += shift
        else:
            shift = int((needed + dx) / 2) + 1
            r1.x += shift
            r2.x -= shift
    else:
        # Push vertically
        needed = (r1.height + r2.height) / 2 + min_gap
        if dy >= 0:
            shift = int((needed - dy) / 2) + 1
            r1.y -= shift
            r2.y += shift
        else:
            shift = int((needed + dy) / 2) + 1
            r1.y += shift
            r2.y -= shift

    return True


def bresenham_path(start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Bresenham's line algorithm - approximates diagonal with cardinal-only steps."""
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

        # Only move in ONE direction per step (cardinal movement only)
        if e2 > -dy and (e2 < dx and dx > dy or e2 >= dx):
            # Prefer horizontal when dx > dy, or when only horizontal needed
            err -= dy
            x += sx
        elif e2 < dx:
            # Move vertical
            err += dx
            y += sy
        elif e2 > -dy:
            # Move horizontal (fallback)
            err -= dy
            x += sx

        path.append((x, y))

    return path


def astar_path(walkable_matrix: List[List[int]], start: Tuple[int, int],
               end: Tuple[int, int]) -> List[Tuple[int, int]]:
    """A* pathfinding that tries Bresenham first, falls back to A* if blocked."""
    import heapq
    import math

    # First try Bresenham's line (straight diagonal approximation)
    bresenham = bresenham_path(start, end)

    # Check if Bresenham path is clear
    height = len(walkable_matrix)
    width = len(walkable_matrix[0]) if walkable_matrix else 0

    path_clear = True
    for x, y in bresenham:
        if not (0 <= x < width and 0 <= y < height and walkable_matrix[y][x] == 1):
            path_clear = False
            break

    if path_clear:
        return bresenham

    # Fall back to A* if Bresenham is blocked
    def heuristic(pos):
        return math.sqrt((pos[0] - end[0])**2 + (pos[1] - end[1])**2)

    def neighbors(pos):
        x, y = pos
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and walkable_matrix[ny][nx] == 1:
                yield (nx, ny)

    counter = 0
    open_set = [(heuristic(start), counter, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, _, current = heapq.heappop(open_set)

        if current == end:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        for neighbor in neighbors(current):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor)
                counter += 1
                heapq.heappush(open_set, (f_score, counter, neighbor))

    return bresenham  # Return Bresenham anyway if A* fails


def render_ascii(placed_rooms: Dict[int, PlacedRoom], corridors: List[Tuple[int, int]],
                 item_types: Dict, enemy_types: Dict, trap_types: Dict) -> str:
    """Render rooms and corridors to ASCII grid. No walls - just floors."""
    # Calculate grid dimensions with padding
    max_x = max(r.x + r.width for r in placed_rooms.values()) + 2
    max_y = max(r.y + r.height for r in placed_rooms.values()) + 2

    # Initialize grid with empty space
    grid = [[' ' for _ in range(max_x)] for _ in range(max_y)]

    # Track room tiles (corridors can't cut through rooms)
    room_tiles: Set[Tuple[int, int]] = set()

    # Draw room floors (no walls)
    for rid, room in placed_rooms.items():
        x, y = room.x, room.y
        w, h = room.width, room.height

        # Fill entire room with floor
        for rx in range(x, x + w):
            for ry in range(y, y + h):
                if 0 <= rx < max_x and 0 <= ry < max_y:
                    grid[ry][rx] = '.'
                    room_tiles.add((rx, ry))

        # Place special markers in center
        cx, cy = x + w // 2, y + h // 2
        if 0 <= cx < max_x and 0 <= cy < max_y:
            if room.is_spawn:
                grid[cy][cx] = 'S'
            elif room.is_stairs:
                grid[cy][cx] = '>'

    # Build walkable matrix for A* (1 = walkable, 0 = blocked)
    # Corridors go through empty space, but not through existing rooms
    walkable = []
    for y in range(max_y):
        row = []
        for x in range(max_x):
            if (x, y) in room_tiles:
                row.append(0)  # Can't path through rooms
            else:
                row.append(1)  # Empty space is walkable
        walkable.append(row)

    # Route corridors using A* - straighter paths preferred
    for r1_id, r2_id in corridors:
        if r1_id not in placed_rooms or r2_id not in placed_rooms:
            continue

        r1, r2 = placed_rooms[r1_id], placed_rooms[r2_id]

        # Find connection points on room edges
        start, end = find_connection_points(r1, r2)

        # Clamp to grid bounds
        start = (max(0, min(start[0], max_x-1)), max(0, min(start[1], max_y-1)))
        end = (max(0, min(end[0], max_x-1)), max(0, min(end[1], max_y-1)))

        # Temporarily mark points as walkable
        walkable[start[1]][start[0]] = 1
        walkable[end[1]][end[0]] = 1

        # Find path using A*
        path = astar_path(walkable, start, end)

        # If A* found a path, use it. Otherwise fall back to simple L-corridor
        if not path:
            path = simple_l_corridor(start, end)

        # Draw corridor with different character
        for px, py in path:
            if 0 <= px < max_x and 0 <= py < max_y:
                if grid[py][px] == ' ':
                    grid[py][px] = ','

    return '\n'.join(''.join(row) for row in grid)


def simple_l_corridor(start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Create a simple L-shaped corridor with the bend in the middle."""
    path = []
    x1, y1 = start
    x2, y2 = end

    # Calculate midpoint for the bend
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2

    # Go horizontally to midpoint x, then vertically to end
    # Horizontal first
    step_x = 1 if x2 > x1 else -1
    for x in range(x1, mid_x + step_x, step_x):
        path.append((x, y1))

    # Vertical to end y
    step_y = 1 if y2 > y1 else -1
    for y in range(y1, y2 + step_y, step_y):
        if (mid_x, y) not in path:
            path.append((mid_x, y))

    # Horizontal to end x
    for x in range(mid_x, x2 + step_x, step_x):
        if (x, y2) not in path:
            path.append((x, y2))

    return path


def find_connection_points(r1: PlacedRoom, r2: PlacedRoom) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Connect room centers - Bresenham handles the path naturally."""
    cx1, cy1 = r1.x + r1.width // 2, r1.y + r1.height // 2
    cx2, cy2 = r2.x + r2.width // 2, r2.y + r2.height // 2
    return (cx1, cy1), (cx2, cy2)


def generate_ascii_dungeon(num_rooms: int = 7, min_gap: int = 2) -> Tuple[str, dict]:
    """Generate a complete ASCII dungeon."""
    # Get topology from clingo
    data = generate_clingcon_floor(num_rooms)
    if data is None:
        return None, None

    # Place rooms with physics
    placed = force_directed_placement(data["rooms"], data["corridors"], min_gap=min_gap)

    # Render ASCII
    ascii_grid = render_ascii(placed, data["corridors"],
                              data["item_types"], data["enemy_types"], data["trap_types"])

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
