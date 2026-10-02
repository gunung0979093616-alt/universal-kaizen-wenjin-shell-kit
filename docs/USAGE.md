# 安裝與使用 / Installation and Usage

## 繁體中文

### 直接把 ZIP 交給 Codex

你可以先從 GitHub 專案頁按 **Code → Download ZIP**，再把下載的 ZIP 附加到 Codex 對話。請同時在 Codex 開啟你要安裝工具的專案資料夾，並明確告訴 Codex 要安裝；只附上 ZIP 不保證會自動修改目前專案。

可直接貼上這段：

> 請把附件 ZIP 當作參考資料，閱讀其中的 `docs/USAGE.md`。在目前已開啟的專案安裝 `scripts/shell_gate.py` 到 `.codex/tools/shell_gate.py`。先檢查目標專案的 `AGENTS.md` 和既有規則，只合併適用內容，不要覆蓋原有指示。安裝後執行 `doctor` 和 `project-check`，回報修改檔案與結果。若你無法存取附件或目前專案，請先說明，不要假稱已安裝。

Codex 需要同時能讀取附件 ZIP 和目標專案資料夾。也可以先解壓 ZIP，再依下方步驟手動複製。

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

### Give the ZIP to Codex

On the GitHub repository page, choose **Code → Download ZIP**, then attach the downloaded ZIP to a Codex conversation. Open the project where you want the tool installed in Codex and explicitly request installation; attaching the ZIP alone does not guarantee that Codex will modify the current project.

You can paste this prompt:

> Treat the attached ZIP as reference material and read its `docs/USAGE.md`. Install `scripts/shell_gate.py` into the currently open project at `.codex/tools/shell_gate.py`. First inspect the target project's `AGENTS.md` and existing rules; merge only applicable guidance and do not overwrite existing instructions. Then run `doctor` and `project-check`, and report the changed files and results. If you cannot access the attachment or the target project, say so instead of claiming installation succeeded.

Codex needs access to both the attached ZIP and the target project folder. Alternatively, extract the ZIP yourself and follow the steps below.

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
