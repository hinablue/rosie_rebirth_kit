"""Compare two JSON archive artifacts without changing either one."""
from __future__ import annotations

from pathlib import Path

from scripts.common.hashes import sha256_json
from scripts.common.io_safe import read_json


def run(left_path: Path, right_path: Path) -> dict[str, object]:
    left, right = read_json(left_path), read_json(right_path)
    keys = sorted(set(left) | set(right))
    changed = [key for key in keys if left.get(key) != right.get(key)]
    return {"schema_version": 1, "left_sha256": sha256_json(left), "right_sha256": sha256_json(right), "changed_keys": changed, "equal": not changed}
