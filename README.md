# 通用 Codex 穩健交付工具包

[English](README.en.md)

專案名稱以 `universal` 說明可攜範圍、`kaizen-wenjin` 說明方法、`shell-kit` 說明交付形式；GitHub repository 名稱使用小寫與連字號，方便閱讀、搜尋與輸入。

這是一個可複製到任何程式專案的輕量工具包；不含任何客戶資料、API 金鑰、品牌、網址或特定雲端平台設定。

它把三件事接在一起：

1. **Kaizen（改善）**：一次只做一個可驗證的小修改。
2. **穩進（Wenjin）**：先盤點、定義保留行為與驗證範圍，再修改；新功能不能破壞已通過流程。
3. **Shell 執行守門**：用實際命令取得退出碼、輸出和時間戳，而不是讓模型口頭宣稱成功。


## 授權

本專案採用 **MIT License（MIT 授權）**。完整條款請見 [`LICENSE`](LICENSE)。MIT 授權允許商業使用、修改、散布、私有使用與再授權，但必須保留著作權與授權聲明，並依授權條款接受免責聲明。

## 公開專案邊界

本儲存庫只包含通用工程工具與文件，不包含特定產品的商業核心、客戶資料、API 金鑰、OAuth 密鑰、部署憑證或第三方服務帳密。

穩進目前是**交付／治理規則與驗證流程**，不是會自行判斷所有情況並自動回退、修復或放行的完整自治控制器。

## 安裝到另一個 Codex 專案

1. 解壓此 ZIP 到安全位置。
2. 將 `AGENTS.md` 的「通用交付守門」段落合併到目標專案既有的 `AGENTS.md`；**不要覆蓋**既有專案指示。
3. 將 `scripts/shell_gate.py` 複製到目標專案，例如 `.codex/tools/shell_gate.py`。
4. 在目標專案先執行：

```bash
python3 .codex/tools/shell_gate.py doctor --cwd .
python3 .codex/tools/shell_gate.py project-check --cwd .
```

完整安裝與使用範例見 [`docs/USAGE.md`](docs/USAGE.md)。

這兩項唯讀，不會修改原始碼、Git 或部署。

## 使用時機與三者差異

| 元件 | 解決的問題 | 何時使用 | 不做什麼 |
| --- | --- | --- | --- |
| Kaizen | 一次改太大、難找回歸 | 每個修改拆成最小可驗證步驟 | 不替代測試或部署驗證 |
| 穩進 | 修 A 壞 B、未知相依與假完成 | 修改既有流程、工具、資料或部署前 | 不取代各專案既有測試 |
| Shell 守門 | 「看起來成功」但未真實執行 | 安裝、測試、建置、Git、ZIP、HTTP 驗證 | 不自動繞過安全確認或執行任意破壞命令 |

正確順序是：**穩進盤點 → Kaizen 最小變更 → Shell 真實驗證 → 穩進跨流程回歸與部署證據**。

## Shell 守門

### 唯讀環境與專案檢查

```bash
python3 scripts/shell_gate.py doctor --cwd .
python3 scripts/shell_gate.py project-check --cwd .
```

輸出會包含工作目錄、作業系統、Python、Git、套件管理器、Git 分支與提交、偵測到的依賴／建置／測試設定。

### 實際執行測試或建置

```bash
python3 scripts/shell_gate.py run --cwd . -- python3 -m pytest -q
python3 scripts/shell_gate.py run --cwd . -- npm test
python3 scripts/shell_gate.py run --cwd . -- npm run build
```

每次執行會在目標專案 `.codex-shell-evidence/` 寫入 JSON 證據：實際 argv、目錄、開始／結束時間、退出碼、stdout、stderr、結果與風險分類。敏感字樣會遮罩。

### ZIP 與 HTTP 健康檢查

```bash
python3 scripts/shell_gate.py zip --cwd . --output /tmp/my-project.zip
python3 scripts/shell_gate.py http --url https://example.invalid/health
```

`zip` 排除 `.env`、私鑰、Git、依賴快取與既有證據目錄，並重新開啟 ZIP 驗證完整性。`http` 只在取得 2xx/3xx 時成功。

### 安全限制

- 指令一律以 argv 執行，**不使用 `shell=True`**。
- `rm -rf`、強制推送、`git reset --hard`、破壞性資料庫指令會被阻擋。
- 會寫入的命令、Git 寫入、部署與可能刪除資料的操作會標示風險；需要目標專案自己的確認流程才可執行。
- 工具包不保存金鑰。輸出中的常見 token、password、secret、Authorization 值會遮罩。
- 失敗會保存 `FAILED` 證據；它不會把失敗改稱成功，也不會無限重跑。

## 失敗處理

先閱讀同一次 evidence 的 `stderr` 與 `exit_code`。只修正可證明原因，再用完全相同命令重新執行。修復循環最多由專案工作流程明確設定次數；不要刪測試、降低斷言或改用假輸出。

## 導入後的驗收

```bash
python3 -m unittest discover -s tests -v
python3 scripts/shell_gate.py doctor --cwd .
python3 scripts/shell_gate.py project-check --cwd .
```

在目標專案再跑它本來的 focused test、跨流程回歸、CI、部署後 health／主要 API 驗證。只有每一層有真實證據才可宣稱完成。

## 邊界

此工具包提供可攜的執行與證據底座，不會替任何專案自動提交、推送、部署、寫資料庫或使用第三方憑證。這些動作必須由該專案明確的授權、範圍與守門決定。
