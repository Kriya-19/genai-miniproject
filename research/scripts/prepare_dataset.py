from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.lib import load_cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and normalize a DiagnoSure JSONL dataset.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    cases = load_cases(args.input)
    seen: set[str] = set()
    with args.output.open("w", encoding="utf-8") as handle:
        for case in cases:
            if case["id"] in seen:
                raise ValueError(f"duplicate case id: {case['id']}")
            seen.add(case["id"])
            handle.write(json.dumps(case, ensure_ascii=False) + "\n")
    print(json.dumps({"cases": len(cases), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
