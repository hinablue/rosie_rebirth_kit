"""Apply only explicitly approved, non-core restore actions with transaction backups."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from scripts.common.hashes import sha256_file
from scripts.common.io_safe import read_json, require_within, write_json
from scripts.common.provenance import utc_now


def run(plan_path: Path, source_root: Path, target_root: Path, tier: str, transaction_log: Path) -> dict[str, object]:
    plan = read_json(plan_path)
    if not plan.get("approved", False):
        raise PermissionError("Restore plan is not explicitly approved")
    if tier == "T0_core":
        raise PermissionError("T0_core restoration is human-only and never automated")
    transaction_id, entries = str(uuid.uuid4()), []
    for action in plan.get("actions", []):
        if action["tier"] != tier or action["operation"] != "create":
            continue
        relative = Path(action["target"])
        source, target = require_within(source_root, source_root / relative), require_within(target_root, target_root / relative)
        if not source.is_file():
            raise FileNotFoundError(source)
        backup = None
        before = sha256_file(target) if target.exists() else None
        if target.exists():
            backup_path = target_root / ".rebirth-backups" / transaction_id / relative
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_path)
            backup = backup_path.relative_to(target_root).as_posix()
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        entries.append({"transaction_id": transaction_id, "action_id": action["action_id"], "target": relative.as_posix(), "before_sha256": before, "after_sha256": sha256_file(target), "backup_path": backup, "created_at": utc_now(), "status": "applied"})
    result = {"schema_version": 1, "transaction_id": transaction_id, "entries": entries}
    write_json(transaction_log, result)
    return result
