#!/usr/bin/env python3
"""Visualize dungeon topology as a graph."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import networkx as nx
import matplotlib.pyplot as plt
from topology import generate_topology, Topology


def visualize_graph(topology: Topology, output_file: str = "pmd_graph.png"):
    """Create a graph visualization of room topology."""
    if topology is None:
        print("No topology to visualize")
        return None

    G = nx.Graph()
    for rid in topology.rooms:
        G.add_node(rid)
    for r1, r2 in topology.connections:
        G.add_edge(r1, r2)

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Position rooms at grid coordinates
    pos = {rid: (room.gx, room.gy) for rid, room in topology.rooms.items()}

    # Draw background grid
    for i in range(topology.grid_size):
        for j in range(topology.grid_size):
            rect = plt.Rectangle((i - 0.45, j - 0.45), 0.9, 0.9,
                                  fill=False, edgecolor='#ddd', linewidth=1, linestyle='--')
            ax.add_patch(rect)
            ax.text(i - 0.4, j - 0.35, f"({i},{j})", fontsize=7, color='#aaa', ha='left', va='bottom')

    # Node colors
    node_colors = []
    for rid in G.nodes():
        room = topology.rooms[rid]
        if room.is_spawn:
            node_colors.append("#4CAF50")
        elif room.is_stairs:
            node_colors.append("#FF9800")
        else:
            node_colors.append("#2196F3")

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#888', width=2, alpha=0.7)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=2500, alpha=0.9)

    # Labels
    labels = {}
    for rid, room in topology.rooms.items():
        lines = [f"R{rid}", f"({room.gx},{room.gy})", f"{room.width}x{room.height}"]
        if room.is_spawn:
            lines.append("SPAWN")
        if room.is_stairs:
            lines.append("STAIRS")
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

    ax.set_title(f"Dungeon Graph\n{len(topology.rooms)} rooms, {len(topology.connections)} corridors",
                fontsize=14, fontweight="bold")

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#4CAF50', label='Spawn'),
        Patch(facecolor='#FF9800', label='Stairs'),
        Patch(facecolor='#2196F3', label='Room'),
    ]
    ax.legend(handles=legend_elements, loc='upper left')

    ax.set_xlim(-0.6, topology.grid_size - 0.4)
    ax.set_ylim(-0.6, topology.grid_size - 0.4)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Saved to {output_file}")
    return output_file


if __name__ == "__main__":
    num_rooms = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    output = sys.argv[2] if len(sys.argv) > 2 else "pmd_graph.png"

    print(f"Generating {num_rooms}-room dungeon graph...")
    topology = generate_topology(num_rooms)
    if topology:
        visualize_graph(topology, output)
