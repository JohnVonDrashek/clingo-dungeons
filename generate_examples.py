#!/usr/bin/env python3
"""Generate example dungeon outputs - both graph PNGs and ASCII text files."""

import sys
sys.path.insert(0, "pmd")

from visualize_graph import visualize_graph, print_graph_info
from render_ascii import generate_ascii_dungeon
from generate_clingcon import generate_clingcon_floor

NUM_EXAMPLES = 10
NUM_ROOMS = 7


def main():
    print(f"Generating {NUM_EXAMPLES} dungeon examples ({NUM_ROOMS} rooms each)...")
    print()

    for i in range(1, NUM_EXAMPLES + 1):
        num = f"{i:02d}"

        # Generate graph PNG
        data = generate_clingcon_floor(NUM_ROOMS)
        if data:
            visualize_graph(data, f"output/graph/dungeon_{num}.png")

        # Generate ASCII text
        ascii_grid, _ = generate_ascii_dungeon(NUM_ROOMS)
        if ascii_grid:
            with open(f"output/ascii/dungeon_{num}.txt", "w") as f:
                f.write(ascii_grid)
            print(f"  output/ascii/dungeon_{num}.txt")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
