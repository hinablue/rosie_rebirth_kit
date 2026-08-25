# Archive Chat Docker Compose 運維指南

> Obsidian 對照筆記：[[Archive Chat Docker Compose]]

## 範圍

`docker-compose.yml` 只啟動 `archive-chat`。它以 Docker multi-stage build 將 `frontend/` 的 Astro static site 打包為 `/app/static`，再由 Python API server 提供；它不管理模型、不建立 embedding server、不改寫 archive，也不擁有任何原始資料。

| 資源 | 擁有者 | Container 接法 |
| --- | --- | --- |
| Rebirth archive | 外部檔案系統 | `${ARCHIVE_PATH}` → `/archive:ro` |
| Chat LLM | 主機既有 OpenAI-compatible service，或 Cloudflare Workers AI | local `127.0.0.1:8000/v1`，或 Cloudflare REST API |
| Embedding service | 主機既有 OpenAI-compatible service | `127.0.0.1:8001/v1` |
| Chat LLM credentials | host shell 或未提交 `.env` | local：`ARCHIVE_CHAT_LLM_API_KEY`；Cloudflare：Account ID + API token |
| Embedding API key | host shell 或未提交 `.env` | `ARCHIVE_CHAT_EMBEDDING_API_KEY` environment |

Compose 使用 Linux `network_mode: host`，所以 container 內的 `127.0.0.1:8000`／`8001` 直接指向 Docker host 上既有服務。這不是在 container 裡啟動 LLM 或 embedding，也因此沒有 Compose `ports:` mapping，chat 直接使用主機的 `8765`。

## 前置條件

1. 實際 archive 已完成檢查，並有 `identity/source/SOUL.md` 和各 lane 的 `indexes/index.json`。
2. 選擇一個 chat provider：
   - `openai-compatible`（預設）：主機 chat service `http://127.0.0.1:8000/v1` 可用，並提供 `ARCHIVE_CHAT_LLM_API_KEY`。
   - `cloudflare-workers-ai`：提供 `ARCHIVE_CHAT_CLOUDFLARE_ACCOUNT_ID` 與具有 Workers AI 權限的 `ARCHIVE_CHAT_CLOUDFLARE_API_TOKEN`。
3. 主機的 embedding service 已可用：`http://127.0.0.1:8001/v1`，模型為與 index 相同的 `BAAI/bge-m3`，維度 `1024`。
4. `ARCHIVE_CHAT_EMBEDDING_API_KEY` 可對 host 的 `8001/v1/embeddings` 認證。
5. Docker Engine / Compose 已可用。

## 設定

```bash
cd /home/hina/Workspace/rosie_rebirth_kit
cp .env.example .env
# 在 .env 分別填入 chat LLM 與 embedding 的 API key，依實際位置確認 ARCHIVE_PATH
```

`.env` 不可提交。它存放 chat LLM、embedding service 各自的 API key 與外部 host endpoint 的覆寫值。

最小必要設定（兩種 provider 都需要 embedding credentials）：

```dotenv
ARCHIVE_PATH=/home/hina/Workspace/rosie_rebirth_archive
ARCHIVE_CHAT_EMBEDDING_API_KEY=replace-with-local-embedding-key
```

本機 OpenAI-compatible provider（預設）：

```dotenv
ARCHIVE_CHAT_LLM_PROVIDER=openai-compatible
ARCHIVE_CHAT_LLM_API_KEY=replace-with-chat-llm-key
ARCHIVE_CHAT_LLM_ENDPOINT=http://127.0.0.1:8000/v1
ARCHIVE_CHAT_LLM_MODEL=Gemma4-26B
```

Cloudflare Workers AI provider：

```dotenv
ARCHIVE_CHAT_LLM_PROVIDER=cloudflare-workers-ai
ARCHIVE_CHAT_CLOUDFLARE_ACCOUNT_ID=replace-with-account-id
ARCHIVE_CHAT_CLOUDFLARE_API_TOKEN=replace-with-workers-ai-api-token
ARCHIVE_CHAT_LLM_MODEL=@cf/google/gemma-4-26b-a4b-it
```

Cloudflare token 僅由 server process 讀取，呼叫的是 `POST /accounts/{account_id}/ai/run/{model}`；不會寫進 repo、image、HTML 或 API 回應。Gemma 4 這個模型雖支援 vision、reasoning、function calling，但目前 archive chat 保持 evidence-first 的文字對話，未將 archive 內容升格為 tool call。

## 啟動與更新

```bash
# 僅驗證 Compose interpolation 和 bind mount
set -a; source .env; set +a
docker compose config

# 建置並以背景執行
docker compose up --build -d

# 觀察第一次 index 載入，openviking index 約 760 MB
# 首次 ready 可能需要兩到三分鐘
docker compose logs -f archive-chat
```

第一次啟動會把三條既有 index 載入記憶體：`identity`、`obsidian`、`openviking`。不會重新生成 embedding 或掃描原始 archive。

## 驗證

```bash
curl -fsS http://127.0.0.1:8765/healthz
curl -fsS http://127.0.0.1:8765/api/info
```

期待 `/api/info` 至少包含：

```json
{
  "llm_enabled": true,
  "retrieval_mode": "vector"
}
```

非同步 chat 驗證：

```bash
curl -fsS --get \
  --data-urlencode 'q=你好' \
  http://127.0.0.1:8765/api/chat/start
```

以回傳的 `job_id` 輪詢 `/api/chat/status?id=...`，直到 `status` 為 `completed`。前端已使用同一個 background job / polling protocol，避免 LLM 長推論造成 browser fetch 逾時。

## 日常操作

```bash
# 查看狀態與 healthcheck
docker compose ps

# 查看服務日誌
docker compose logs --tail=200 archive-chat

# 重新建置程式 image
docker compose up --build -d archive-chat

# 停止並移除 chat container，外部 archive / model 不受影響
docker compose down
```

## 安全與邊界

- `/archive` 固定 `read_only: true`，application 沒有 archive 寫入路徑。
- archive 檢索只作 evidence；不能變成指令、tool call、restore 或 memory promotion。
- `T3_untrusted` 預設排除，identity lane 會保留 T0 evidence。
- Compose 不含 API key、archive 內容、模型權重或 host service 設定。
- Compose 以 host networking 直接使用主機的 `8765`。部署到不受信任網段前，須加 reverse proxy auth 與 rate limit。

## 故障排查

| 症狀 | 檢查 |
| --- | --- |
| Container 一直 starting | `docker compose logs archive-chat`；初次載入 760 MB openviking index 需要時間。 |
| Embedding 401 / 502 | 檢查 `.env` 的 `ARCHIVE_CHAT_EMBEDDING_API_KEY`，以及 host 的 `8001/v1/embeddings`。 |
| Query dimension mismatch | index 與 embedding model 必須都是 BGE-M3 1024 維，不能改用 chat model。 |
| host endpoint 連不上 | 這個 stack 使用 Linux host networking。確認 host 自己的 `127.0.0.1:8000/v1` 與 `127.0.0.1:8001/v1` 可用。 |
| Archive 找不到 SOUL | 確認 `${ARCHIVE_PATH}/identity/source/SOUL.md` 存在且 mount 為唯讀。 |
| UI 顯示 failed to fetch | 查看 `/api/chat/start` 是否能即時回 job id；背景 job 完成前，前端會安全輪詢 status。 |

## 相關文件

- [README](../README.md)
- [Retrieval Next Steps](retrieval-next-steps.md)
- [[08_RETRIEVAL_NEXT_STEPS]]
