#!/usr/bin/env python3
"""
Visualize dungeon as a simple graph - rooms as nodes, corridors as edges.
No spatial/pixel placement - just topology with dimensions as labels.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import networkx as nx
import matplotlib.pyplot as plt
from generate_clingcon import generate_clingcon_floor


def visualize_graph(data, output_file="pmd_graph.png"):
    """Create a simple graph visualization - just topology, no spatial placement."""
    if data is None:
        print("No data to visualize")
        return None

    rooms = data.get("rooms", {})
    corridors = data.get("corridors", [])

    G = nx.Graph()

    # Add nodes
    for rid in rooms:
        G.add_node(rid)

    # Add edges
    for r1, r2 in corridors:
        G.add_edge(r1, r2)

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Get grid size from data or default to 4
    grid_size = data.get("grid_size", 4)

    # Use actual grid positions instead of spring layout
    pos = {}
    for rid in G.nodes():
        room = rooms[rid]
        # Position rooms at their grid coordinates
        # Flip Y so (0,0) is bottom-left
        pos[rid] = (room.gx, room.gy)

    # Draw the background grid
    for i in range(grid_size):
        for j in range(grid_size):
            rect = plt.Rectangle((i - 0.45, j - 0.45), 0.9, 0.9,
                                  fill=False, edgecolor='#ddd', linewidth=1, linestyle='--')
            ax.add_patch(rect)
            # Grid coordinate label in corner
            ax.text(i - 0.4, j - 0.35, f"({i},{j})", fontsize=7, color='#aaa', ha='left', va='bottom')

    # Node colors based on room type
    node_colors = []
    for rid in G.nodes():
        room = rooms[rid]
        if room.is_spawn:
            node_colors.append("#4CAF50")  # Green
        elif room.is_stairs:
            node_colors.append("#FF9800")  # Orange
        else:
            node_colors.append("#2196F3")  # Blue

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#888', width=2, alpha=0.7)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=2500, alpha=0.9)

    # Build labels with room info
    labels = {}
    for rid in G.nodes():
        room = rooms[rid]
        lines = [f"R{rid}"]
        lines.append(f"({room.gx},{room.gy})")
        lines.append(f"{room.width}x{room.height}")

        if room.is_spawn:
            lines.append("SPAWN")
        if room.is_stairs:
            lines.append("STAIRS")

        # Content summary
        content = []
        if room.items:
            content.append(f"{len(room.items)} items")
        if room.enemies:
            content.append(f"{len(room.enemies)} enemies")
        if room.traps:
            content.append(f"{len(room.traps)} traps")
        if content:
            lines.append(", ".join(content))

        labels[rid] = "\n".join(lines)

    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=8, font_weight='bold')

    # Title
    ax.set_title(f"Dungeon Graph\n{len(rooms)} rooms, {len(corridors)} corridors",
                fontsize=14, fontweight="bold")

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#4CAF50', label='Spawn'),
        Patch(facecolor='#FF9800', label='Stairs'),
        Patch(facecolor='#2196F3', label='Room'),
    ]
    ax.legend(handles=legend_elements, loc='upper left')

    # Set axis limits to show the full grid with padding
    ax.set_xlim(-0.6, grid_size - 0.4)
    ax.set_ylim(-0.6, grid_size - 0.4)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Saved to {output_file}")
    return output_file


def print_graph_info(data):
    """Print graph information as text."""
    if data is None:
        print("No data")
        return

    rooms = data.get("rooms", {})
    corridors = data.get("corridors", [])
    item_types = data.get("item_types", {})
    enemy_types = data.get("enemy_types", {})
    trap_types = data.get("trap_types", {})

    print("=" * 50)
    print("DUNGEON GRAPH")
    print("=" * 50)
    print(f"\nRooms: {len(rooms)}")
    print(f"Corridors: {len(corridors)}")
    print()

    print("ROOMS:")
    for rid in sorted(rooms.keys()):
        room = rooms[rid]
        role = ""
        if room.is_spawn:
            role = " [SPAWN]"
        elif room.is_stairs:
            role = " [STAIRS]"

        print(f"  Room {rid}: ({room.gx},{room.gy}) {room.width}x{room.height}{role}")

        if room.items:
            items = [item_types.get(i, "?") for i in room.items]
            print(f"    Items: {', '.join(items)}")
        if room.enemies:
            enemies = [enemy_types.get(e, "?") for e in room.enemies]
            print(f"    Enemies: {', '.join(enemies)}")
        if room.traps:
            traps = [trap_types.get(t, "?") for t in room.traps]
            print(f"    Traps: {', '.join(traps)}")
    print()

    print("CONNECTIONS:")
    for r1, r2 in corridors:
        print(f"  Room {r1} <-> Room {r2}")
    print()


if __name__ == "__main__":
    num_rooms = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    output = sys.argv[2] if len(sys.argv) > 2 else "pmd_graph.png"

    print(f"Generating {num_rooms}-room dungeon graph...")
    data = generate_clingcon_floor(num_rooms)

    if data:
        print_graph_info(data)
        visualize_graph(data, output)
