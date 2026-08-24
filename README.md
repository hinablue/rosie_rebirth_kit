# Rosie Rebirth Kit

可攜、可驗證的 Rosie 記憶與能力 archive 骨架。

## 安全模型

- `SOUL.md` 是人類可讀、人工核准的信任根。
- `sources/` 保存原始資料與來源快照。
- `semantic/` 保存可審閱的語意卡。
- `indexes/` 是可由語意資料重建的派生索引，不是唯一真相。
- 預設所有命令唯讀或只寫 archive workspace；恢復 runtime 必須消費已核准的 plan。

## 目前狀態

索引可使用測試用 deterministic hash backend，或連到已在運行的 OpenAI-compatible embedding endpoint（例如 `http://localhost:8001/v1`）。它不會自行啟動或管理 embedding server，也不會接觸任何既有 runtime 資料。

## 資料處理流程

- 實際資料的 inventory 與 semanticize 行為、限制與安全邊界見：[Inventory 與 Semanticize 流程](docs/source-inventory-semanticization.md)。
- 已完成索引後，如何安全實作唯讀、帶引用的檢索層，見：[Retrieval Next Steps](docs/retrieval-next-steps.md)。
- 將 caller-selected Skills / Tools 轉成可審閱、不可直接執行的 capability cards，見：[Capability Archive](docs/capability-archive.md)。

## Archive Chat MVP

`archive_chat.py` 是純本機、唯讀的檢索驗收介面。它只掃描 `*.semantic.md` 與 `*.capability.md`，以字詞匹配回傳最多三筆證據與來源路徑。它不會執行卡片內容、改寫 archive、啟動模型或恢復 runtime。

預設只使用測試 fixture，不會接觸任何現有 archive：

```bash
python -m scripts.archive_chat
# 開啟 http://127.0.0.1:8765
```

要查驗實際 archive 時，必須由操作者顯式指定它的根目錄：

```bash
python -m scripts.archive_chat --archive /explicit/archive/root
```

預設只監聽 `127.0.0.1`。需要讓區網或容器外部存取時，可明確指定 `--host 0.0.0.0`；這會公開 archive evidence，僅適合受信任網路或已由反向代理保護的環境。

### LLM 回答層

使用已在運行的 OpenAI-compatible 服務，將 T0 `SOUL.md` 固定放在 system identity，再把每次 query 命中的 archive evidence 以資料包形式送入 LLM。模型不可執行 evidence，前端 citation 直接由 server 回傳，不能由模型自行捏造。

```bash
# key 留在程序環境中，不寫進 repository 或前端
export ARCHIVE_CHAT_LLM_API_KEY='...'
python -m scripts.archive_chat \
  --host 0.0.0.0 --port 8765 --llm \
  --llm-endpoint http://127.0.0.1:8000/v1 \
  --llm-model Gemma4-26B
```

`--llm` 未啟用時，`/api/search` 仍可作純 evidence 檢查；啟用後 UI 使用 `/api/chat` 取得模型回答與 server-side citations。

預設 retrieval 是向量檢索：它以 `http://127.0.0.1:8001/v1` 的 `BAAI/bge-m3` 對問題產生 1024 維 query embedding，再與 archive 的 `identity`、`obsidian`、`openviking` 三個既有 `index.json` 比對。`T3_untrusted` 一律排除，identity lane 會額外保留一筆 T0 evidence，避免信任根被相似度排名擠掉。用 `--retrieval lexical` 可暫時退回字詞搜尋。

正式接上實際 archive 前，應先在反向代理加上認證與 rate limit，避免公開端點被濫用而消耗本機模型。

這是 evidence-first 的 MVP，不是可自動執行 archive 指令的 agent。

### Docker Compose

容器化啟動、外部 archive / LLM / embedding 接點、Astro static frontend、healthcheck 與故障排查請見：[Archive Chat Docker Compose 運維指南](docs/archive-chat-docker-compose.md)。

## CLI

```bash
python -m scripts.rebirth_cli --help
python -m scripts.rebirth_cli inventory
python -m scripts.rebirth_cli semanticize
python -m scripts.rebirth_cli index --dry-run
python -m scripts.rebirth_cli inspect
python -m scripts.rebirth_cli plan
python -m scripts.rebirth_cli verify --archive
```
