"""CLI entry point for the placeholder rebirth toolchain."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_index, inspect_runtime, inventory_sources, plan_restore, semanticize, verify_rebirth


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Rosie Rebirth Kit scaffold")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("inventory")
    subparsers.add_parser("semanticize")
    index = subparsers.add_parser("index")
    index.add_argument("--dry-run", action="store_true")
    subparsers.add_parser("inspect")
    subparsers.add_parser("plan")
    verify = subparsers.add_parser("verify")
    verify.add_argument("--archive", action="store_true")
    args = parser.parse_args()
    root = project_root()
    if args.command == "inventory":
        print(json.dumps(inventory_sources.run(root, root / "sources/manifest.json"), ensure_ascii=False, indent=2))
    elif args.command == "semanticize":
        print(semanticize.run(root, root / "semantic"))
    elif args.command == "index":
        print(json.dumps(build_index.run(root / "semantic", root / "indexes/embedding-v1", dry_run=args.dry_run), ensure_ascii=False, indent=2))
    elif args.command == "inspect":
        print(json.dumps(inspect_runtime.run(root / "runtime/runtime-report.json"), ensure_ascii=False, indent=2))
    elif args.command == "plan":
        print(json.dumps(plan_restore.run(root / "sources/manifest.json", root / "runtime/runtime-report.json"), ensure_ascii=False, indent=2))
    elif args.command == "verify":
        failures = verify_rebirth.verify_archive(root)
        print("OK" if not failures else "\n".join(failures))
        return 0 if not failures else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
