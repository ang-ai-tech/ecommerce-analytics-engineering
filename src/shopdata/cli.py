"""Command line: `shopdata generate`."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from shopdata.generator import generate


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="shopdata", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    gen = commands.add_parser("generate", help="write the raw CSV files")
    gen.add_argument("--out", type=Path, default=Path("data/raw"))
    gen.add_argument("--seed", type=int, default=42)
    gen.add_argument(
        "--until",
        type=datetime.fromisoformat,
        help="only data known at this date, e.g. 2026-06-30 (to try incremental loads)",
    )
    args = parser.parse_args(argv)

    counts = generate(args.out, seed=args.seed, until=args.until)
    for name, rows in counts.items():
        print(f"{name:<12} {rows:>7} rows -> {args.out / (name + '.csv')}")


if __name__ == "__main__":
    main()
