from pathlib import Path

import pytest

from scripts.common.io_safe import require_within


def test_require_within_rejects_escape(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        require_within(tmp_path, tmp_path / ".." / "outside")
