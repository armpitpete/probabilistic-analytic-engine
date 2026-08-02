"""Command-line interface for PAE structured assessments."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .acquisition import AcquisitionError
from .engine import assess_case


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Assess evidence coverage and structure without calculating probabilities."
    )
    command.add_argument("case", type=Path, help="Path to a PAE case JSON file")
    command.add_argument("--output", type=Path, help="Optional output JSON path")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        case = json.loads(args.case.read_text(encoding="utf-8"))
        result = assess_case(case)
    except (OSError, json.JSONDecodeError, AcquisitionError) as exc:
        print(f"PAE assessment failed: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
