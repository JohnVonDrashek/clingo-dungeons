#!/usr/bin/env python3
"""Generate example dungeon outputs - both graph PNGs and ASCII text files."""

import sys
sys.path.insert(0, "pmd")

from visualize_graph import visualize_graph
from render_ascii import render_ascii
from generate_clingcon import generate_clingcon_floor, generate_dungeon

NUM_EXAMPLES = 10
NUM_ROOMS = 7


def main():
    print(f"Generating {NUM_EXAMPLES} dungeon examples ({NUM_ROOMS} rooms each)...")
    print()

    for i in range(1, NUM_EXAMPLES + 1):
        num = f"{i:02d}"

        # Generate graph PNG (uses topology only)
        data = generate_clingcon_floor(NUM_ROOMS)
        if data:
            visualize_graph(data, f"output/graph/dungeon_{num}.png")

        # Generate ASCII text (uses full dungeon calculation)
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
