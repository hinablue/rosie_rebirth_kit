"""Launch a local llama.cpp embedding server for an explicit GGUF model path."""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def command(model: Path, *, host: str = "127.0.0.1", port: int = 8088, gpu_layers: int = 0, context_size: int = 8192) -> list[str]:
    binary = shutil.which("llama-server")
    if binary is None:
        raise FileNotFoundError("llama-server is not installed or not on PATH")
    if not model.is_file() or model.suffix.lower() != ".gguf":
        raise ValueError(f"Expected an existing .gguf embedding model: {model}")
    return [binary, "--model", str(model), "--embedding", "--host", host, "--port", str(port), "--ctx-size", str(context_size), "--gpu-layers", str(gpu_layers)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch llama.cpp with a GGUF embedding model")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument("--gpu-layers", type=int, default=0)
    parser.add_argument("--context-size", type=int, default=8192)
    args = parser.parse_args()
    subprocess.run(command(args.model, host=args.host, port=args.port, gpu_layers=args.gpu_layers, context_size=args.context_size), check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
