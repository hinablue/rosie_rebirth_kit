"""Create a portable zip bundle, excluding private source records by default."""
from __future__ import annotations

import zipfile
from pathlib import Path

from scripts.common.io_safe import read_json, write_json


def run(source_root: Path, manifest_path: Path, destination: Path, *, include_private: bool = False) -> dict[str, object]:
    manifest = read_json(manifest_path)
    included: list[str] = []
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for record in manifest.get("sources", []):
            if record.get("private", False) and not include_private:
                continue
            path = source_root / str(record["relative_path"])
            if not path.is_file():
                raise FileNotFoundError(path)
            arcname = f"sources/{record['relative_path']}"
            bundle.write(path, arcname)
            included.append(arcname)
        bundle.writestr("manifest.json", __import__("json").dumps({"schema_version": 1, "included": included}, ensure_ascii=False, indent=2))
    return {"archive": str(destination), "included": included, "private_included": include_private}
