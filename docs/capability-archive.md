# Capability Archive：Skills 與 Tools 的可攜轉換

## 目的與邊界

Capability Archive 是 `identity`、`obsidian`、`openviking` 之外的獨立 archive lane。它保存「某項能力的來源、目的、輸入／輸出提示、約束、adapter 候選與驗證方式」，不把目前 Hermes runtime 的特定工具名當成跨環境保證。

它不是：

- 對 Obsidian / OpenViking 記憶資料的重複掃描；
- 可直接執行的工具清單；
- 自動安裝 Skill、註冊 Tool、啟動服務或搬移 runtime 設定；
- 原始 Skill / Tool 檔案的完整複製品。

來源必須由操作者明確指定。程式只讀取允許的文字檔、寫出 derived artifact，並排除 symbolic link、`.git`、虛擬環境、cache、`node_modules` 與名稱含 secret / token / credentials 的路徑元件。

## 實作模組

| 模組 | 作用 | 副作用 |
| --- | --- | --- |
| `capability_inventory.py` | 對明確指定的 Skill / Tool root 建立 SHA-256、來源 URI、mtime 與 tier manifest | 僅寫 manifest |
| `build_capability_cards.py` | 從 manifest 讀取受控 metadata，產生可審閱 capability Markdown card | 僅寫 cards 與 card manifest |
| `verify_capabilities.py` | 驗證來源 hash、card ↔ source 對應、必要 frontmatter 與生成 card 中的秘密標記 | 唯讀 |

Capability card 不會嵌入完整原始內容；它只抽取 Skill 的 frontmatter／標題或 Tool JSON 的 `name`、`description`、parameter property 名稱。這避免將未審閱指令或意外秘密放入可攜 card。

## Trust policy

`capability-inventory` 預設以 `T2_observed` 封裝。只有在操作者已完成人工審閱時，才可明確傳入 `--trust-tier T1_curated`。腳本不能自動把來源提升成 T1，也不能接受 `T0_core` 或 `T3_untrusted` 作為 capability source tier。

每張 card 都固定包含：

- `source_uri`、`source_sha256`、`source_id`；
- purpose、inputs、outputs；
- 不可直接執行的 constraints；
- preferred adapter 與保守的 `unavailable` fallback；
- 在目標 runtime 重新 discovery、再做非破壞 smoke test 的 verification 要求。

完成 conversion 後，card 可用既有 `build_index.py` 建立 index；indexer 會讀取 `.semantic.md` 與 `.capability.md`，但 index 仍只是可重建的衍生物。

## 建議 archive 位置

```text
/home/hina/Workspace/rosie_rebirth_archive/
├── identity/       # T0 信任根
├── obsidian/       # 記憶與專案資料
├── openviking/     # 記憶與資源資料
└── capabilities/
    ├── derived/
    ├── cards/
    └── indexes/
```

不要把 `capabilities/index.json` 與其他 lane 的 index 合併。轉生時先讀 `identity`，再以 capability index 判斷可用 adapter，最後才使用 Obsidian / OpenViking 作背景證據。

## 範例流程

以下所有路徑都只是範例，沒有預設掃描主機資料：

```bash
python -m scripts.rebirth_cli capability-inventory \
  --skills-source /explicit/skills \
  --tools-source /explicit/tool-schemas \
  --trust-tier T2_observed \
  --output /explicit/archive/capabilities/derived/sources.json

# 人工審閱 manifest 後
python -m scripts.rebirth_cli capability-cards \
  --manifest /explicit/archive/capabilities/derived/sources.json \
  --output-dir /explicit/archive/capabilities/cards \
  --cards /explicit/archive/capabilities/derived/capability-cards.json

python -m scripts.rebirth_cli capability-verify \
  --manifest /explicit/archive/capabilities/derived/sources.json \
  --cards /explicit/archive/capabilities/derived/capability-cards.json \
  --cards-dir /explicit/archive/capabilities/cards

# 選擇已在運行的 embedding backend 後
python -m scripts.rebirth_cli index \
  --semantic-dir /explicit/archive/capabilities/cards \
  --output-dir /explicit/archive/capabilities/indexes
```

`capability-cards` 會在讀取來源時重新比對 manifest 的 SHA-256；來源在 inventory 與 card build 間有任何異動就會拒絕產生 card。這項完整性門檻比既有 `semanticize.py` 更嚴格。

## 現行限制

- Tool source 目前是 caller-supplied JSON / Markdown / YAML / TOML / Python text source；尚未有 Hermes runtime tool-catalog adapter。
- `preferred_adapters` 目前來自來源宣告的名稱，是候選而非安裝或可用性證明。
- 沒有自動 fallback 推理、能力去重、跨卡衝突裁決或 runtime adapter discovery。
- 未建立 retrieval regression 前，不應把 capability index 接到自動決策或 runtime mutation。
