"""Minimal clingo wrapper for dungeon generation."""

from pathlib import Path
from collections import defaultdict
import clingo


def solve(
    lp_files: list[str | Path],
    extra_facts: str = "",
    constants: dict[str, int | str] | None = None,
    num_solutions: int = 1,
) -> list[dict]:
    """
    Solve ASP program and return parsed solutions.

    Args:
        lp_files: List of .lp file paths to load
        extra_facts: Additional facts to add (e.g., from previous layer)
        constants: Dict of constant overrides (e.g., {"num_rooms": 10})
        num_solutions: Number of solutions to find (0 = all)

    Returns:
        List of solutions, each a dict mapping predicate names to list of arg tuples
    """
    solutions = []

    def on_model(model):
        atoms = defaultdict(list)
        for atom in model.symbols(shown=True):
            name = atom.name
            args = tuple(
                arg.number if arg.type == clingo.SymbolType.Number else str(arg)
                for arg in atom.arguments
            )
            atoms[name].append(args if args else True)
        solutions.append(dict(atoms))

    # Build command line args
    args = [f"-n{num_solutions}"]
    if constants:
        for name, value in constants.items():
            args.append(f"-c {name}={value}")

    ctl = clingo.Control(args)

    # Load .lp files
    for lp_file in lp_files:
        ctl.load(str(lp_file))

    # Add extra facts if provided
    if extra_facts:
        ctl.add("extra", [], extra_facts)
        ctl.ground([("base", []), ("extra", [])])
    else:
        ctl.ground([("base", [])])

    ctl.solve(on_model=on_model)

    return solutions


def solve_files(*lp_files: str | Path, **kwargs) -> list[dict]:
    """Convenience wrapper for solve() with positional file args."""
    return solve(list(lp_files), **kwargs)


def facts_from_solution(solution: dict, predicates: list[str] | None = None) -> str:
    """
    Convert a solution dict back to ASP facts for chaining layers.

    Args:
        solution: Solution dict from solve()
        predicates: If provided, only include these predicates

    Returns:
        String of ASP facts
    """
    lines = []
    for name, args_list in solution.items():
        if predicates and name not in predicates:
            continue
        for args in args_list:
            if args is True:
                lines.append(f"{name}.")
            else:
                args_str = ",".join(str(a) for a in args)
                lines.append(f"{name}({args_str}).")
    return "\n".join(lines)


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        solutions = solve(sys.argv[1:])
        for i, sol in enumerate(solutions):
            print(f"=== Solution {i+1} ===")
            for name, args in sorted(sol.items()):
                print(f"  {name}: {args}")
    else:
        print("Usage: python runner.py file1.lp [file2.lp ...]")
