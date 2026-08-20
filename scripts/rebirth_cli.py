"""Command line interface. All source selection is explicit; no command targets current data by default."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_index, inspect_runtime, inventory_sources, plan_restore, semanticize, verify_rebirth


def _print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Rosie Rebirth Kit")
    sub = parser.add_subparsers(dest="command", required=True)
    inventory = sub.add_parser("inventory", help="Inventory an explicit source directory")
    inventory.add_argument("--source", type=Path, required=True)
    inventory.add_argument("--output", type=Path, required=True)
    semantic = sub.add_parser("semanticize", help="Build semantic cards from an explicit manifest")
    semantic.add_argument("--source", type=Path, required=True)
    semantic.add_argument("--manifest", type=Path, required=True)
    semantic.add_argument("--output-dir", type=Path, required=True)
    semantic.add_argument("--cards", type=Path, required=True)
    index = sub.add_parser("index", help="Build an index from semantic cards")
    index.add_argument("--semantic-dir", type=Path, required=True)
    index.add_argument("--output-dir", type=Path, required=True)
    index.add_argument("--dry-run", action="store_true")
    inspect = sub.add_parser("inspect", help="Write a read-only runtime report")
    inspect.add_argument("--output", type=Path, required=True)
    plan = sub.add_parser("plan", help="Write a no-side-effect restore plan")
    plan.add_argument("--manifest", type=Path, required=True)
    plan.add_argument("--runtime", type=Path, required=True)
    plan.add_argument("--output", type=Path, required=True)
    verify = sub.add_parser("verify", help="Verify an archive workspace")
    verify.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "inventory": _print(inventory_sources.run(args.source, args.output))
    elif args.command == "semanticize": _print(semanticize.run(args.source, args.manifest, args.output_dir, args.cards))
    elif args.command == "index": _print(build_index.run(args.semantic_dir, args.output_dir, dry_run=args.dry_run))
    elif args.command == "inspect": _print(inspect_runtime.run(args.output))
    elif args.command == "plan": _print(plan_restore.run(args.manifest, args.runtime, args.output))
    else:
        failures = verify_rebirth.verify_archive(args.root)
        _print({"ok": not failures, "failures": failures})
        return 0 if not failures else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
