# GGUF Embedding Backend

Production embeddings use an **already-running OpenAI-compatible embedding server**. It may be a local `llama.cpp`/`llama-server` process, a Docker service, or a reachable network service. The indexer never loads a GGUF model directly and never starts or manages an embedding server.

## Prerequisites

1. Select a dedicated embedding model appropriate to the server. A chat/GGUF model is not automatically a suitable embedding model.
2. Have an OpenAI-compatible server running and obtain its API root or explicit embeddings URL.

### Optional: launch a local llama.cpp server

This helper is only for environments where Rebirth Kit should own the server launch. It is **not** required when another process already supplies embeddings.

```bash
python -m scripts.serve_embedding_gguf \
  --model /absolute/path/to/embedding-model.gguf \
  --port 8088 \
  --gpu-layers 99
```

Before indexing real material, verify `/v1/models` and a minimal `/v1/embeddings` request directly. Rebirth Kit accepts both an API root (for example `http://localhost:8001/v1`) and the explicit embeddings route.

## Indexer configuration

```bash
export REBIRTH_EMBEDDING_KIND=openai-compatible
export REBIRTH_EMBEDDING_ENDPOINT=http://localhost:8001/v1
export REBIRTH_EMBEDDING_MODEL=bge-m3-Q8_0.gguf
# Optional: set only when this particular server requires authentication.
export REBIRTH_EMBEDDING_API_KEY=local-not-secret
```

`REBIRTH_EMBEDDING_KIND=llama.cpp` remains accepted as a compatibility alias, but it no longer implies that Rebirth Kit launches `llama-server`.

`HashEmbeddingBackend` remains available only for deterministic unit tests and dry development. It is not a semantic embedding model and must not be used for a production archive.
