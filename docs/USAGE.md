# 安裝與使用 / Installation and Usage

## 繁體中文

### 1. 下載與安裝

可從 GitHub repository 選 **Code → Download ZIP**，或使用 Git：

```bash
git clone https://github.com/gunung0979093616-alt/universal-kaizen-wenjin-shell-kit.git
```

把 `scripts/shell_gate.py` 複製到目標專案，例如 `.codex/tools/shell_gate.py`。將 `AGENTS.md` 範本中適用的通用守門規則合併到目標專案現有指示；不要覆蓋原有規則。只使用標準 Python 函式庫，不需安裝第三方 Python 套件。

### 2. 先盤點目標專案

```bash
python3 .codex/tools/shell_gate.py doctor --cwd .
python3 .codex/tools/shell_gate.py project-check --cwd .
```

這兩個命令只讀取環境與專案結構。`doctor` 顯示 Python、Git 與常見工具資訊；`project-check` 顯示依賴、建置、測試與 Git 狀態。

### 3. 執行命令並留下證據

唯讀命令可直接執行：

```bash
python3 .codex/tools/shell_gate.py run --cwd . -- python3 -m pytest -q
```

可能修改檔案的命令需要明確加上 `--allow-write`，仍須遵守目標專案自己的授權與審查流程：

```bash
python3 .codex/tools/shell_gate.py run --cwd . --allow-write -- npm test
```

執行紀錄會寫到目標專案的 `.codex-shell-evidence/`，包含命令、目錄、時間、退出碼與輸出。不要把含有機密或個人資料的輸出分享或提交。

### 4. 建立並檢查 ZIP

```bash
python3 .codex/tools/shell_gate.py zip --cwd . --output /tmp/project-delivery.zip
```

工具會排除常見機密檔案、Git 目錄、依賴快取及既有證據，並檢查 ZIP 完整性。建立後仍應人工確認封存內容符合交付範圍。

### 5. 檢查 HTTP 端點

```bash
python3 .codex/tools/shell_gate.py http --url https://example.com/health
```

HTTP 檢查只代表該網址回應 2xx/3xx，不代表應用程式的所有功能都正常。

### 6. 在本工具包執行自我驗證

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_kit.py
python3 scripts/shell_gate.py doctor --cwd .
python3 scripts/shell_gate.py project-check --cwd .
```

## English

### 1. Download and install

On GitHub, choose **Code → Download ZIP**, or clone the repository:

```bash
git clone https://github.com/gunung0979093616-alt/universal-kaizen-wenjin-shell-kit.git
```

Copy `scripts/shell_gate.py` into the target project, for example `.codex/tools/shell_gate.py`. Merge only the relevant generic rules from this kit's `AGENTS.md` into the target project's existing instructions; do not overwrite its existing rules. The tool uses only the Python standard library.

### 2. Inspect the target project first

```bash
python3 .codex/tools/shell_gate.py doctor --cwd .
python3 .codex/tools/shell_gate.py project-check --cwd .
```

These commands only inspect the environment and project structure. `doctor` reports Python, Git, and common tools. `project-check` reports dependency, build, test, and Git information.

### 3. Run a command and record evidence

Read-only commands can run directly:

```bash
python3 .codex/tools/shell_gate.py run --cwd . -- python3 -m pytest -q
```

Commands that may write files require the explicit `--allow-write` flag and must still follow the target project's own authorization and review process:

```bash
python3 .codex/tools/shell_gate.py run --cwd . --allow-write -- npm test
```

Execution records are written to `.codex-shell-evidence/` in the target project and include the command, directory, timestamps, exit code, and output. Do not share or commit output containing secrets or personal data.

### 4. Create and verify a ZIP

```bash
python3 .codex/tools/shell_gate.py zip --cwd . --output /tmp/project-delivery.zip
```

The tool excludes common secret files, Git data, dependency caches, and prior evidence, then verifies ZIP integrity. Manually review the archive to confirm it contains only files intended for delivery.

### 5. Check an HTTP endpoint

```bash
python3 .codex/tools/shell_gate.py http --url https://example.com/health
```

An HTTP check only confirms that the URL returned a 2xx/3xx response; it does not prove that every application feature works.

### 6. Verify this toolkit

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_kit.py
python3 scripts/shell_gate.py doctor --cwd .
python3 scripts/shell_gate.py project-check --cwd .
```
