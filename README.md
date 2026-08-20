# Rosie Rebirth Kit

可攜、可驗證的 Rosie 記憶與能力 archive 骨架。

## 安全模型

- `SOUL.md` 是人類可讀、人工核准的信任根。
- `sources/` 保存原始資料與來源快照。
- `semantic/` 保存可審閱的語意卡。
- `indexes/` 是可由語意資料重建的派生索引，不是唯一真相。
- 預設所有命令唯讀或只寫 archive workspace；恢復 runtime 必須消費已核准的 plan。

## 目前狀態

此專案目前只建立可編譯的 placeholder；尚未接入 embedding provider、OpenViking 或任何 runtime 寫入介面。

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
