# Security Policy

This policy is also provided in 繁體中文 below.

## Scope

This repository contains a portable command-execution and evidence toolkit. It is designed to reduce the risk of treating unverified model output as execution proof.

## Do not disclose secrets

Never include the following in issues, pull requests, commits, ZIP archives, or test fixtures:

- API keys or access tokens
- OAuth client secrets or refresh tokens
- Passwords
- Private keys or certificates containing private key material
- Database credentials
- Deployment credentials
- Customer or personal data

## Reporting a vulnerability

For a suspected security vulnerability, avoid publishing exploitable details in a public issue. Contact the repository maintainer privately through the contact method associated with the GitHub account that maintains this repository.

When reporting, include the affected file or command, reproduction steps that do not expose secrets, expected behavior, observed behavior, and potential impact.

## Security limitations

The Shell Gate is a safety-oriented command runner, not a complete sandbox or operating-system security boundary. Do not treat its command filters as a substitute for OS permissions, container isolation, CI security controls, or project-specific authorization.

## 繁體中文

### 適用範圍

本 repository 包含可攜式命令執行與證據工具，目標是避免把未驗證的模型輸出當成執行證明。

### 請勿公開機密

請勿在 issue、pull request、commit、ZIP 或測試資料中放入 API 金鑰、access token、OAuth 密鑰、密碼、私鑰、資料庫或部署憑證、客戶或個人資料。

### 回報安全漏洞

請勿在公開 issue 張貼可利用細節。請透過 GitHub 維護者帳號的私下聯絡方式通報，附上受影響檔案或命令、不含機密的重現步驟、預期與實際行為及可能影響。

### 安全限制

Shell Gate 是以安全為目標的命令執行器，不是完整沙箱或作業系統安全邊界。命令過濾不能取代作業系統權限、容器隔離、CI 安全控制或各專案自己的授權流程。
