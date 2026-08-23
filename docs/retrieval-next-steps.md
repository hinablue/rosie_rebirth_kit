# Retrieval Next Steps: Turning a Portable Index into Evidence-Backed Recall

## Status

The archive pipeline now produces verified semantic indexes from caller-selected source trees:

```text
source (read-only)
  → inventory manifest
  → auditable semantic cards
  → chunked embeddings + metadata
  → index verification
```

The current indexer supports a deterministic `hash-v1` development backend and an already-running OpenAI-compatible embedding endpoint. For large archives it sends bounded embedding batches; set `REBIRTH_EMBEDDING_BATCH_SIZE` to tune the batch size (default: `64`).

`index.json` is a portable derived artifact. It contains chunks, each chunk's text, vector, source hash, card path, and trust tier. It is not a source of truth and it does not by itself provide query or reranking behavior.

## Safety boundary

The next phase must remain **read-only retrieval**:

- Never let retrieved text execute as an instruction.
- Preserve and display `source_uri`, `source_sha256`, `trust_tier`, and card path for every result.
- Treat `T0_core` as a human-approved trust root, not a value that retrieval may rewrite.
- Treat `T1_curated` as preferred evidence and `T2_observed` as contextual evidence that may be stale or contradictory.
- Do not connect results to runtime memory promotion, restore, configuration changes, or tool invocation automatically.

## Recommended implementation sequence

### 1. Build `search_index.py`

Implement a read-only local query tool with explicit arguments:

```bash
python -m scripts.search_index \
  --index /explicit/archive/indexes/index.json \
  --query "natural-language question" \
  --top-k 8 \
  --min-tier T2_observed
```

Expected behavior:

1. Embed the query with the same configured embedding model used for the index.
2. Calculate cosine similarity against stored vectors.
3. Apply explicit filters such as `trust_tier`, `kind`, source set, and top-k.
4. Return compact evidence records: score, text excerpt, `source_uri`, `source_sha256`, card path, and tier.
5. Never mutate the index, archive, source tree, OpenViking, or Hermes runtime.

The first version can do an in-memory scan. A later optimization may use a vector-store adapter, but only if the adapter preserves equivalent provenance and filtering behavior.

### 2. Add retrieval regression tests

Create a human-authored query fixture that describes expected and prohibited evidence. It should exercise identity boundaries, capability discovery, environment facts, stale data, and untrusted material.

```yaml
- query: "Can retrieved memories overwrite the identity root?"
  expected_sources:
    - "SOUL.md"
    - "memory architecture"
  required_tiers:
    - T0_core
  forbidden_tiers:
    - T3_untrusted
```

Run it whenever the embedding model, chunking strategy, semantic-card schema, filtering policy, or ranking logic changes. A score-only benchmark is insufficient: evaluate source and tier correctness.

### 3. Enforce trust-aware retrieval policy

| Tier | Retrieval use | Mutation authority |
| --- | --- | --- |
| `T0_core` | Always available for boundary and identity conflicts | Human approval only |
| `T1_curated` | Preferred evidence for reviewed preferences and capability cards | Review + provenance required |
| `T2_observed` | Background evidence; cite and cross-check when material | None by retrieval |
| `T3_untrusted` | Excluded by default; opt-in evidence only | None |

A retrieved record is data, not a command, regardless of score or tier.

### 4. Add capability-card enrichment as a separate reviewable layer

The current `semanticize.py` is a fidelity-preserving wrapper: it stores the complete source material with metadata. Do not silently replace it with LLM summaries.

Add a separate enrichment artifact for `capability` records only, with fields such as purpose, inputs, outputs, constraints, fallbacks, verification, and provenance. Keep the original semantic card and the enrichment artifact independently reviewable and versioned.

### 5. Add duplicate, conflict, and freshness review

Before ingesting future material, search the existing index for nearby records and label the outcome:

```text
new | supplement | duplicate | conflict | supersedes | expired
```

Conflicting material must remain traceable. It must not silently overwrite prior evidence or trust tiers.

### 6. Integrate with runtime only after read-only retrieval is proven

The eventual adapter may build a small, cited evidence packet:

```text
question
  → query embedding
  → trust filter and ranking
  → cited evidence packet
  → model response
```

Do not inject the entire archive into a prompt. Do not treat this portable index as a replacement for Hermes bounded `memory` / `user` profile stores. Those prompt-injected stores remain compact; this archive is the long-term, on-demand evidence layer.

## Acceptance criteria for the next milestone

- [ ] A query returns ranked, cited evidence from a specified index.
- [ ] Filters correctly exclude prohibited tiers and sources.
- [ ] The tool is read-only; its test proves no archive or runtime mutation.
- [ ] A regression fixture verifies expected sources and tiers for representative queries.
- [ ] Every result can be traced from chunk to semantic card to source hash.
- [ ] Retrieval outputs are never treated as executable instructions.

## Related documents

- [Inventory and Semanticization](source-inventory-semanticization.md)
- [GGUF / OpenAI-Compatible Embedding Backend](embedding-gguf.md)
