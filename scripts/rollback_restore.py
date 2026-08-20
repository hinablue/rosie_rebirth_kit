"""Rollback a transaction created by restore_tier, verifying post-write hashes."""
from __future__ import annotations

import shutil
from pathlib import Path

from scripts.common.hashes import sha256_file
from scripts.common.io_safe import read_json


def run(transaction_log: Path, target_root: Path) -> dict[str, object]:
    transaction, restored = read_json(transaction_log), []
    for entry in reversed(transaction.get("entries", [])):
        target = target_root / str(entry["target"])
        if target.exists() and sha256_file(target) != entry["after_sha256"]:
            raise RuntimeError(f"Refusing rollback; target changed since transaction: {target}")
        backup = entry.get("backup_path")
        if backup:
            source = target_root / str(backup)
            if not source.is_file():
                raise FileNotFoundError(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif target.exists():
            target.unlink()
        restored.append(str(entry["target"]))
    return {"transaction_id": transaction.get("transaction_id"), "restored": restored}
