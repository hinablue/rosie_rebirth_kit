"""Generate review-required restoration plans without writing a target runtime."""
from __future__ import annotations

from pathlib import Path

from scripts.common.hashes import sha256_file, sha256_json
from scripts.common.io_safe import read_json, write_json
from scripts.common.provenance import utc_now


def plan_restore(manifest: dict[str, object], runtime: dict[str, object]) -> dict[str, object]:
    actions: list[dict[str, object]] = []
    capabilities = dict(runtime.get("capabilities", {}))
    for source in manifest.get("sources", []):
        if not isinstance(source, dict):
            raise ValueError("Malformed source manifest")
        provenance = dict(source["provenance"])
        tier = str(provenance["trust_tier"])
        operation = "review" if tier == "T0_core" else "index_only"
        reason = "Trust root needs explicit approval" if tier == "T0_core" else "Semantic archive is retrieved, not directly injected"
        actions.append({"action_id": f"restore:{source['id']}", "tier": tier, "target": str(source["relative_path"]), "operation": operation, "reason": reason, "source_ids": [str(source["id"])], "requires_human_approval": True, "status": "planned"})
    return {"schema_version": 1, "plan_id": sha256_json(actions)[:16], "created_at": utc_now(), "runtime_can_write": bool(capabilities.get("filesystem_write", False)), "actions": actions, "requires_human_approval": True}


def run(manifest_path: Path, runtime_report_path: Path, output: Path) -> dict[str, object]:
    manifest, runtime = read_json(manifest_path), read_json(runtime_report_path)
    result = plan_restore(manifest, runtime)
    result["manifest_sha256"] = sha256_file(manifest_path)
    result["runtime_report_sha256"] = sha256_file(runtime_report_path)
    write_json(output, result)
    return result
