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
