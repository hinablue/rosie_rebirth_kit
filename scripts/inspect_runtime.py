"""Read-only discovery of target runtime capabilities."""
from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import sys
from pathlib import Path

from scripts.common.io_safe import write_json
from scripts.common.provenance import utc_now

KNOWN_TOOLS = ("git", "python3", "uv", "docker", "gh")
KNOWN_MODULES = ("sentence_transformers", "openai", "pydantic")


def inspect_runtime() -> dict[str, object]:
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "python": {"version": sys.version, "executable": sys.executable},
        "platform": platform.platform(),
        "capabilities": {"filesystem_read": True, "filesystem_write": os.access(Path.cwd(), os.W_OK), "network_configured": bool(os.getenv("REBIRTH_EMBEDDING_ENDPOINT"))},
        "tools": {tool: shutil.which(tool) is not None for tool in KNOWN_TOOLS},
        "modules": {module: importlib.util.find_spec(module) is not None for module in KNOWN_MODULES},
    }


def run(output: Path) -> dict[str, object]:
    report = inspect_runtime()
    write_json(output, report)
    return report
