from pathlib import Path

import pytest

from scripts.serve_embedding_gguf import command


def test_gguf_server_requires_binary_and_real_model(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.serve_embedding_gguf.shutil.which", lambda _: "/usr/bin/llama-server")
    model = tmp_path / "embed.gguf"
    model.write_bytes(b"gguf")
    result = command(model, port=9999, gpu_layers=5)
    assert result[0] == "/usr/bin/llama-server"
    assert "--embedding" in result
    assert "9999" in result
