# Contributing

English and 繁體中文 guidelines are provided below.

Thank you for contributing.

## Change principles

- Keep each change small and verifiable.
- Preserve existing behavior unless the change explicitly requires otherwise.
- Add or update tests for changed behavior.
- Do not remove tests or weaken assertions to make a change pass.
- Do not add secrets, customer data, credentials, or private project information.
- Use the Shell Gate to record real execution evidence where applicable.

## Before submitting a change

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_kit.py
python3 scripts/shell_gate.py doctor --cwd .
python3 scripts/shell_gate.py project-check --cwd .
```

Describe what changed, what behavior must remain unchanged, and the evidence produced by the verification commands.

## 繁體中文

### 修改原則

- 每次只做小而可驗證的修改。
- 除非需求明確要求，否則保留既有行為。
- 修改行為時新增或更新測試。
- 不得刪除測試或降低斷言來讓檢查通過。
- 不得加入機密、客戶資料、憑證或私人專案資訊。
- 適用時使用 Shell Gate 記錄實際執行證據。

### 提交前

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_kit.py
python3 scripts/shell_gate.py doctor --cwd .
python3 scripts/shell_gate.py project-check --cwd .
```

請說明變更內容、必須保留的行為，以及驗證命令產生的證據。
