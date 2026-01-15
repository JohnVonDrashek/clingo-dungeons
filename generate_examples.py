#!/usr/bin/env python3
"""Generate example dungeon outputs - both graph PNGs and ASCII text files."""

import sys
sys.path.insert(0, "pmd")

from topology import generate_topology
from visualize_graph import visualize_graph
from dungeon import generate_dungeon
from render_ascii import render_ascii

NUM_EXAMPLES = 10
NUM_ROOMS = 7


def main():
    print(f"Generating {NUM_EXAMPLES} dungeon examples ({NUM_ROOMS} rooms each)...")
    print()

    for i in range(1, NUM_EXAMPLES + 1):
        num = f"{i:02d}"

        # Generate graph PNG (topology only)
        topology = generate_topology(NUM_ROOMS)
        if topology:
            visualize_graph(topology, f"output/graph/dungeon_{num}.png")

        # Generate ASCII text (full pipeline)
        dungeon = generate_dungeon(NUM_ROOMS)
        if dungeon:
            ascii_grid = render_ascii(dungeon)
            with open(f"output/ascii/dungeon_{num}.txt", "w") as f:
                f.write(ascii_grid)
            print(f"  output/ascii/dungeon_{num}.txt")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
