# GGUF Embedding Backend

Production embeddings use a **local GGUF embedding model**, served by `llama.cpp`; the indexer never loads a GGUF model directly.

## Prerequisites

1. Select a dedicated embedding GGUF model compatible with llama.cpp. A chat/GGUF model is not automatically a suitable embedding model.
2. Install `llama-server`.
3. Start the local server with the explicit model path:

```bash
python -m scripts.serve_embedding_gguf \
  --model /absolute/path/to/embedding-model.gguf \
  --port 8088 \
  --gpu-layers 99
```

The server exposes its OpenAI-compatible embeddings route. Before indexing real material, verify `/v1/models` and a minimal `/v1/embeddings` request directly.

## Indexer configuration

```bash
export REBIRTH_EMBEDDING_KIND=llama.cpp
export REBIRTH_EMBEDDING_ENDPOINT=http://127.0.0.1:8088/v1/embeddings
export REBIRTH_EMBEDDING_MODEL=local-embedding-gguf
export REBIRTH_EMBEDDING_API_KEY=local-not-secret
```

`HashEmbeddingBackend` remains available only for deterministic unit tests and dry development. It is not a semantic embedding model and must not be used for a production archive.
