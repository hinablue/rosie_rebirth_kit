from scripts.archive_chat import stream_chat_events


def test_sse_stream_emits_status_then_done() -> None:
    events = list(stream_chat_events(lambda publish: {"answer": "完成"}))

    assert events == [
        ("status", {"phase": "retrieving"}),
        ("done", {"answer": "完成"}),
    ]


def test_sse_done_payload_contains_only_the_public_answer() -> None:
    events = list(stream_chat_events(lambda publish: {"answer": "完成"}))

    assert all(event != "evidence" for event, _payload in events)
    assert events[-1] == ("done", {"answer": "完成"})


def test_sse_stream_converts_worker_failure_to_safe_event() -> None:
    def fail(_publish: object) -> dict[str, object]:
        raise RuntimeError("internal detail")

    events = list(stream_chat_events(fail))

    assert events[-1] == ("failure", {"error": "LLM request failed"})