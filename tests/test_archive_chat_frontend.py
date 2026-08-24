from pathlib import Path


FRONTEND = Path(__file__).parents[1] / "frontend" / "src" / "pages" / "index.astro"


def test_frontend_has_single_request_lock_markdown_and_ttl_storage() -> None:
    source = FRONTEND.read_text(encoding="utf-8")

    assert "setSending(true)" in source
    assert "button.textContent = sending ? \"讀取中…\" : \"送出\"" in source
    assert "query.disabled = sending" in source
    assert "renderMarkdown" in source
    assert "escapeHtml" in source
    assert "<br />" in source
    assert "sessionStorage" in source
    assert "PROFILE_KEY" in source
    assert "name-dialog" in source
    assert "message-label" in source
    assert 'kind === "user" ? displayName' in source
    assert "messages.scrollTop = messages.scrollHeight" in source
    assert "4 * 60 * 60 * 1000" in source
    assert "persistMessage(\"assistant\", data.answer)" in source
    assert "message(entry.role, entry.text, { markdown: true })" in source
    assert "new EventSource" in source
    assert "/api/chat/events" in source
    assert "crypto.randomUUID()" in source
    assert "conversationSession" in source
    assert "addEventListener(\"done\"" in source
    assert "addEventListener(\"failure\"" in source
    assert "/api/chat/status" not in source
    assert "pause(1000)" not in source
    assert "clear-history" in source
    assert "sessionStorage.removeItem(STORAGE_KEY)" in source
    assert "overflow:visible" in source
    assert ".message>.content" in source
    assert "並非 LLM 對話" not in source
