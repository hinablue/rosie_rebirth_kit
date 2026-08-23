# 實際資料的 Inventory 與 Semanticize 流程

本文件描述目前程式碼已實作的行為。它不會自動探索主機資料、不會寫入 runtime，也不會以 LLM 改寫原始資料。

## 邊界與命令

所有來源與輸出位置都必須由操作者明確指定：

```bash
python -m scripts.rebirth_cli inventory \
  --source /明確指定的來源目錄 \
  --exclude-name .obsidian \
  --exclude-name .livesync \
  --output /明確指定的archive/derived/sources.json

python -m scripts.rebirth_cli semanticize \
  --source /同一個來源目錄 \
  --manifest /明確指定的archive/derived/sources.json \
  --output-dir /明確指定的archive/semantic \
  --cards /明確指定的archive/derived/cards.json
```

來源目錄應視為唯讀。Inventory 與 semanticize 的輸出應置於來源根目錄之外的 archive workspace；工具不會自行掃描 `$HOME`、Hermes、OpenViking 或其他 runtime 位置。

## 1. Inventory：來源快照

`inventory_sources.py` 遞迴盤點指定 source root，並只將可接受的文字來源寫入 manifest。

### 納入與排除

- 納入副檔名：`.md`、`.txt`、`.json`、`.yaml`、`.yml`、`.toml`、`.py`。
- 排除 symbolic link，避免來源目錄連結到 workspace 外部或系統檔。
- 排除 binary 與未列在白名單的格式。
- 排除 `.git`、`.venv`、`__pycache__`、`.pytest_cache`、`indexes`、`runtime` 等版本控制、環境、快取與派生內容。
- 可用可重複指定的 `--exclude-name NAME`（舊名 `--exclude-dir` 仍可用）排除名稱相符的檔案或目錄元件，例如 `.obsidian`、`.livesync`、`.livesync-snapshot.json` 或 `_system`。這些 caller-selected exclusions 與預設排除規則會一併生效。

### 每筆來源記錄

manifest 的每筆 record 包含相對路徑、分類、私密標記與 provenance：

```json
{
  "id": "source:skills/example/SKILL.md",
  "relative_path": "skills/example/SKILL.md",
  "kind": "capability",
  "private": true,
  "provenance": {
    "source_uri": "file://skills/example/SKILL.md",
    "source_sha256": "<原始檔內容 SHA-256>",
    "source_mtime_ns": 0,
    "generated_at": "<UTC 時間>",
    "generator_version": "inventory_sources/1",
    "trust_tier": "T1_curated"
  }
}
```

`source_sha256` 是原始內容的 SHA-256，可將後續 semantic card 對應回具體來源版本。Inventory 不修改來源內容，僅原子寫入指定的 JSON manifest。

### 分類與信任層

| 條件 | `kind` | 預設 trust tier |
| --- | --- | --- |
| 檔名 `SOUL.md` | `identity` | `T0_core` |
| 路徑包含 `skill` 或 `skills` | `capability` | `T1_curated` |
| `.py` 檔 | `tooling` | `T2_observed` |
| 其他白名單文字檔 | `memory` | `T2_observed` |

呼叫端可用 `trust_overrides` 覆寫個別相對路徑；未知 tier 會被拒絕。

## 2. Semanticize：可稽核 Markdown card

目前的 `semanticize.py` 是**保真封裝**，不是自動摘要器。它讀取 inventory manifest 中列出的來源，將完整 UTF-8 原文放到可審閱的 semantic Markdown card，並保留來源 metadata。

每筆資料依序會：

1. 從 manifest 取得 `relative_path`。
2. 以 containment check 確認它仍位於指定 source root；路徑跳脫會被拒絕。
3. 讀取原始文字，使用第一個 `# Heading` 作為 card title；沒有 heading 時使用相對路徑。
4. 從 manifest 帶入 `source_uri`、`source_sha256`、`trust_tier` 與 `private`。
5. 將原文寫入 `## Source Material`，輸出到依 `kind` 分類的 `semantic/` 子目錄。
6. 寫出 `cards.json`，列出每張 card 與對應 provenance。

卡片外觀如下：

```md
---
id: semantic:skills/example/SKILL.md
kind: capability
private: True
source_sha256: <原始檔 SHA-256>
source_uri: file://skills/example/SKILL.md
trust_tier: T1_curated
---

# 原始檔標題

## Source Material

<完整原始內容>
```

這讓後續 index 能穩定切 chunk，也讓人可以檢查內容、類型、tier 與來源雜湊，而不必把 vector index 視為唯一真相。

## 現行限制與正確操作

- semanticize 不呼叫 LLM，不會自行抽取「人格事實」、改寫原文或提升信任層級。
- Inventory manifest 記錄 SHA-256；但目前 semanticize **尚未重新計算來源檔 SHA-256 後拒絕不一致**。Inventory 與 semanticize 之間若有來源異動，應重新 inventory。將 hash re-check 設為強制門檻是下一個值得補強的完整性改進。
- `sources.json` 與 `cards.json` 採 atomic write；目前 individual `.semantic.md` card 是直接寫入。中斷不會傷到來源檔，但可能留下不完整 card。
- `SOUL.md` 會被歸為 `T0_core`；即使未來進入 restore lifecycle，也不是可自動覆寫的資料。

## 建議實作順序

```text
來源目錄（唯讀）
  → inventory（sources.json）
  → 人工檢查：來源集合、private 與 trust tier
  → semanticize（semantic/*.semantic.md、cards.json）
  → 人工審閱 card
  → index
  → archive verify
```

在處理真實資料前，先以 fixture 或可拋棄的測試資料走完整流程。