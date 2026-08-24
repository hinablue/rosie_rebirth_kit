from pathlib import Path

import pytest

from scripts.archive_chat import ArchiveChatError, search_archive


FIXTURE_ARCHIVE = Path(__file__).parent / "fixtures" / "chat-demo-archive"


def test_search_returns_cited_evidence_from_explicit_fixture() -> None:
    result = search_archive(FIXTURE_ARCHIVE, "什麼內容不能自動恢復")

    assert result["query"] == "什麼內容不能自動恢復"
    assert result["matches"]
    first = result["matches"][0]
    assert first["path"] == "semantic/identity/soul.semantic.md"
    assert first["trust_tier"] == "T0_core"
    assert "自動" in first["snippet"]


def test_search_rejects_blank_queries() -> None:
    with pytest.raises(ArchiveChatError, match="empty"):
        search_archive(FIXTURE_ARCHIVE, "   ")


def test_search_requires_an_existing_archive_directory(tmp_path: Path) -> None:
    with pytest.raises(ArchiveChatError, match="directory"):
        search_archive(tmp_path / "not-here", "identity")
