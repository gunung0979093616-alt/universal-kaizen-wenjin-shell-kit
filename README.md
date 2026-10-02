# 通用 Codex 穩健交付工具包 / Universal Codex Kaizen · Wenjin · Shell Gate Kit

[English-only README](README.en.md) · [完整安裝與使用指南 / Full installation and usage guide](docs/USAGE.md)

[![Tests](https://github.com/gunung0979093616-alt/universal-kaizen-wenjin-shell-kit/actions/workflows/tests.yml/badge.svg)](https://github.com/gunung0979093616-alt/universal-kaizen-wenjin-shell-kit/actions/workflows/tests.yml)

**繁體中文：**可複製到不同程式專案的輕量工具包，協助把修改拆小、保留既有行為，並留下真實命令執行證據。

**English:** A lightweight toolkit for different software projects. It helps make small changes, preserve existing behavior, and record evidence from real command execution.

## 專案名稱 / Project name

`universal` 是「通用」的意思，表示工具包不綁定單一產品；`kaizen-wenjin` 說明改善與穩進方法；`shell-kit` 說明它提供可攜式 Shell 工具。Repository 名稱採小寫和連字號，方便閱讀與輸入。

`Universal` means the kit is designed for use across projects rather than being tied to one product. `Kaizen-Wenjin` names the improvement and behavior-preservation methods, while `Shell-Kit` describes the portable command-line tool. The repository name uses lowercase words and hyphens for readability.

## 提供什麼 / What it provides

1. **Kaizen（改善） / Kaizen:** 一次完成一個小而可驗證的修改。 / Make one small, verifiable change at a time.
2. **穩進 / Wenjin:** 先盤點現況、定義必須保留的行為，再修改並檢查回歸。 / Inspect the current state and define behavior to preserve before changing and checking for regressions.
3. **Shell 執行守門 / Shell Gate:** 實際執行命令並保存退出碼、輸出、時間和風險分類，不以模型文字代替執行證據。 / Execute commands and record exit codes, output, timestamps, and risk classifications instead of treating model text as proof.

## 使用時機與三者差異 / When to use each part

| 元件 / Component | 解決的問題 / Problem addressed | 何時使用 / When to use it | 不做什麼 / What it does not do |
| --- | --- | --- | --- |
| Kaizen | 一次改太多，難以定位回歸。<br>Changes are too large to review or debug. | 將修改拆成最小可驗證步驟。<br>Break work into small, verifiable steps. | 不替代測試或部署驗證。<br>Does not replace tests or deployment checks. |
| 穩進 / Wenjin | 修 A 壞 B、未知相依或誤報完成。<br>Fixing one thing breaks another; dependencies are unclear; completion is overstated. | 修改既有流程、工具、資料或部署前。<br>Before changing existing workflows, tools, data, or deployments. | 不取代目標專案自己的測試。<br>Does not replace the target project's own tests. |
| Shell 守門 / Shell Gate | 「看起來成功」但命令未實際執行。<br>A command appears successful but was not actually run. | 執行環境檢查、測試、建置、ZIP 或 HTTP 檢查時。<br>For environment checks, tests, builds, ZIP creation, or HTTP checks. | 不繞過安全確認，也不是完整沙箱。<br>Does not bypass authorization and is not a complete sandbox. |

**建議順序 / Suggested sequence:** 穩進盤點 → Kaizen 最小變更 → Shell 真實驗證 → 穩進回歸檢查與部署證據。<br>Wenjin inspection → minimal Kaizen change → real Shell verification → Wenjin regression checks and deployment evidence.

## 安裝與使用 / Installation and usage

### 直接把 ZIP 交給 Codex / Give the ZIP to Codex

從 GitHub 專案頁選 **Code → Download ZIP**，把 ZIP 附加到 Codex 對話，並在 Codex 開啟要安裝工具的目標專案。**只附加 ZIP 不會保證 Codex 自動安裝或修改專案；請明確提出要求。**

On GitHub, choose **Code → Download ZIP**, attach the archive to a Codex conversation, and open the target project in Codex. **Attaching the ZIP alone does not guarantee that Codex will install the tool or modify the project; explicitly ask it to do so.**

可直接複製以下提示 / Copy this prompt:

> 請把附件 ZIP 當作參考資料，閱讀其中的 `docs/USAGE.md`。在目前已開啟的專案安裝 `scripts/shell_gate.py` 到 `.codex/tools/shell_gate.py`。先檢查目標專案的 `AGENTS.md` 和既有規則，只合併適用內容，不要覆蓋原有指示。安裝後執行 `doctor` 和 `project-check`，回報修改檔案與結果。若你無法存取附件或目前專案，請先說明，不要假稱已安裝。

> Treat the attached ZIP as reference material and read its `docs/USAGE.md`. Install `scripts/shell_gate.py` into the currently open project at `.codex/tools/shell_gate.py`. First inspect the target project's `AGENTS.md` and existing rules; merge only applicable guidance and do not overwrite existing instructions. Then run `doctor` and `project-check`, and report the changed files and results. If you cannot access the attachment or the target project, say so instead of claiming installation succeeded.

Codex 必須能存取附件和目標專案資料夾。也可以先解壓 ZIP，再依完整[中英文使用指南](docs/USAGE.md)手動安裝。<br>Codex needs access to both the attachment and the target project folder. Alternatively, extract the ZIP and follow the full [bilingual usage guide](docs/USAGE.md).

### 唯讀環境與專案檢查 / Read-only environment and project checks

```bash
python3 .codex/tools/shell_gate.py doctor --cwd .
python3 .codex/tools/shell_gate.py project-check --cwd .
```

這兩個命令會回報工作目錄、作業系統、Python、Git、常見工具、依賴、建置與測試設定。它們只檢查資訊，不會修改原始碼、Git 或部署。<br>These commands report the working directory, operating system, Python, Git, common tools, dependencies, build configuration, and test setup. They inspect information only and do not modify source code, Git, or deployments.

### 執行測試或建置 / Run tests or builds

```bash
python3 .codex/tools/shell_gate.py run --cwd . -- python3 -m pytest -q
python3 .codex/tools/shell_gate.py run --cwd . -- npm test
python3 .codex/tools/shell_gate.py run --cwd . -- npm run build
```

可能寫入檔案的命令需依 Shell Gate 的提示明確授權，並遵守目標專案自己的審查流程。執行紀錄會寫入目標專案 `.codex-shell-evidence/`，包含命令、目錄、時間、退出碼與輸出；分享前請確認沒有機密或個人資料。<br>Commands that may write files require explicit authorization as indicated by Shell Gate and must follow the target project's review process. Execution records are saved under `.codex-shell-evidence/` in the target project and include the command, directory, timestamps, exit code, and output. Check for secrets or personal data before sharing them.

### ZIP 與 HTTP 檢查 / ZIP and HTTP checks

```bash
python3 .codex/tools/shell_gate.py zip --cwd . --output /tmp/my-project.zip
python3 .codex/tools/shell_gate.py http --url https://example.invalid/health
```

ZIP 命令會排除常見機密檔案、Git、依賴快取與既有證據，並檢查封存完整性；交付前仍應人工檢查內容。HTTP 命令只確認網址回應 2xx/3xx，不代表應用程式所有功能正常。<br>The ZIP command excludes common secret files, Git data, dependency caches, and prior evidence, then checks archive integrity; review the contents before delivery. The HTTP command only confirms a 2xx/3xx response and does not prove that every application feature works.

## 安全限制 / Safety limits

- 指令以 argv 執行，不使用 `shell=True`。<br>Commands run as argv; `shell=True` is not used.
- 破壞性命令會被阻擋；工具不會繞過授權或確認。<br>Destructive commands are blocked; the tool does not bypass authorization or confirmation.
- 常見 token、password、secret 和 Authorization 輸出會遮罩，但這不是完整機密掃描。<br>Common token, password, secret, and Authorization values are redacted, but this is not a complete secret scanner.
- Shell Gate 是輔助工具，不是作業系統權限、容器隔離、CI 控制或專案審查流程的替代品。<br>Shell Gate is an assisting tool, not a replacement for operating-system permissions, container isolation, CI controls, or project review.

## 驗證 / Verification

在本工具包執行 / Run these commands in this repository:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_kit.py
python3 scripts/shell_gate.py doctor --cwd .
python3 scripts/shell_gate.py project-check --cwd .
```

每個 `PASS` 只代表對應檢查有可追溯結果，不單獨代表正式部署安全或完成。<br>Each `PASS` means only that the corresponding check produced traceable results; it does not by itself prove a production deployment is safe or complete.

## 授權與公開範圍 / License and project scope

本專案採 MIT License；完整條款見 [`LICENSE`](LICENSE)。儲存庫只提供通用工程工具與文件，不包含特定產品核心、客戶資料、API 金鑰、OAuth 密鑰、部署憑證或第三方服務帳密。<br>This project uses the MIT License; see [`LICENSE`](LICENSE) for the full terms. The repository contains only generic engineering tools and documentation. It does not include product-specific core systems, customer data, API keys, OAuth secrets, deployment credentials, or third-party account credentials.

穩進目前是交付治理規則與驗證流程，**不是**能自行處理所有情境的自治修復控制器。工具包不會替其他專案自動提交、推送、部署、寫入資料庫或使用第三方憑證。<br>Wenjin is currently a delivery-governance protocol and verification workflow; it is **not** a fully autonomous repair controller. This kit does not automatically commit, push, deploy, write to databases, or use third-party credentials on behalf of other projects.

## 社群與支援 / Community and support

[貢獻指南 / Contributing](CONTRIBUTING.md) · [行為準則 / Code of Conduct](CODE_OF_CONDUCT.md) · [安全政策 / Security](SECURITY.md) · [支援 / Support](SUPPORT.md) · [引用 / Citation](CITATION.cff)
