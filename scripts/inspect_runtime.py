"""Read-only runtime capability inspection."""
from __future__ import annotations

import platform
import sys
from pathlib import Path


def run(output: Path) -> dict[str, object]:
    report = {"schema_version": 1, "python": sys.version, "platform": platform.platform(), "capabilities": {"filesystem_read": True, "filesystem_write": True}, "status": "placeholder"}
    output.parent.mkdir(parents=True, exist_ok=True)
    import json
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
