# Universal Codex Kaizen · Wenjin · Shell Gate Kit

[繁體中文 / Traditional Chinese](README.md) · [Full installation and usage guide / 完整安裝與使用指南](docs/USAGE.md)

[![Tests](https://github.com/gunung0979093616-alt/universal-kaizen-wenjin-shell-kit/actions/workflows/tests.yml/badge.svg)](https://github.com/gunung0979093616-alt/universal-kaizen-wenjin-shell-kit/actions/workflows/tests.yml)

A lightweight toolkit for different software projects. It helps make small changes, preserve existing behavior, and record evidence from real command execution.

## Project name

`Universal` means the kit is designed for use across projects rather than being tied to one product. `Kaizen-Wenjin` names the improvement and behavior-preservation methods, while `Shell-Kit` describes the portable command-line tool. The repository name uses lowercase words and hyphens for readability.

## What it provides

1. **Kaizen:** Make one small, verifiable change at a time.
2. **Wenjin:** Inspect the current state and define behavior to preserve before changing and checking for regressions.
3. **Shell Gate:** Execute commands and record exit codes, output, timestamps, and risk classifications instead of treating model text as proof.

## When to use each part

| Component | Problem addressed | When to use it | What it does not do |
| --- | --- | --- | --- |
| Kaizen | Changes are too large to review or debug. | Break work into small, verifiable steps. | Does not replace tests or deployment checks. |
| Wenjin | Fixing one thing breaks another; dependencies are unclear; completion is overstated. | Before changing existing workflows, tools, data, or deployments. | Does not replace the target project's own tests. |
| Shell Gate | A command appears successful but was not actually run. | For environment checks, tests, builds, ZIP creation, or HTTP checks. | Does not bypass authorization and is not a complete sandbox. |

**Suggested sequence:** Wenjin inspection → minimal Kaizen change → real Shell verification → Wenjin regression checks and deployment evidence.

## Installation and usage

### Give the ZIP to Codex

On GitHub, choose **Code → Download ZIP**, attach the archive to a Codex conversation, and open the target project in Codex. **Attaching the ZIP alone does not guarantee that Codex will install the tool or modify the project; explicitly ask it to do so.**

Copy this prompt:

> Treat the attached ZIP as reference material and read its `docs/USAGE.md`. Install `scripts/shell_gate.py` into the currently open project at `.codex/tools/shell_gate.py`. First inspect the target project's `AGENTS.md` and existing rules; merge only applicable guidance and do not overwrite existing instructions. Then run `doctor` and `project-check`, and report the changed files and results. If you cannot access the attachment or the target project, say so instead of claiming installation succeeded.

Codex needs access to both the attachment and the target project folder. Alternatively, extract the ZIP and follow the full [bilingual usage guide](docs/USAGE.md).

### Read-only environment and project checks

```bash
python3 .codex/tools/shell_gate.py doctor --cwd .
python3 .codex/tools/shell_gate.py project-check --cwd .
```

These commands report the working directory, operating system, Python, Git, common tools, dependencies, build configuration, and test setup. They inspect information only and do not modify source code, Git, or deployments.

### Run tests or builds

```bash
python3 .codex/tools/shell_gate.py run --cwd . -- python3 -m pytest -q
python3 .codex/tools/shell_gate.py run --cwd . -- npm test
python3 .codex/tools/shell_gate.py run --cwd . -- npm run build
```

Commands that may write files require explicit authorization as indicated by Shell Gate and must follow the target project's review process. Execution records are saved under `.codex-shell-evidence/` in the target project and include the command, directory, timestamps, exit code, and output. Check for secrets or personal data before sharing them.

### ZIP and HTTP checks

```bash
python3 .codex/tools/shell_gate.py zip --cwd . --output /tmp/my-project.zip
python3 .codex/tools/shell_gate.py http --url https://example.invalid/health
```

The ZIP command excludes common secret files, Git data, dependency caches, and prior evidence, then checks archive integrity; review the contents before delivery. The HTTP command only confirms a 2xx/3xx response and does not prove that every application feature works.

## Safety limits

- Commands run as argv; `shell=True` is not used.
- Destructive commands are blocked; the tool does not bypass authorization or confirmation.
- Common token, password, secret, and Authorization values are redacted, but this is not a complete secret scanner.
- Shell Gate is an assisting tool, not a replacement for operating-system permissions, container isolation, CI controls, or project review.

## Verification

Run these commands in this repository:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_kit.py
python3 scripts/shell_gate.py doctor --cwd .
python3 scripts/shell_gate.py project-check --cwd .
```

Each `PASS` means only that the corresponding check produced traceable results; it does not by itself prove a production deployment is safe or complete.

## License and project scope

This project uses the MIT License; see [`LICENSE`](LICENSE) for the full terms. The repository contains only generic engineering tools and documentation. It does not include product-specific core systems, customer data, API keys, OAuth secrets, deployment credentials, or third-party account credentials.

Wenjin is currently a delivery-governance protocol and verification workflow; it is **not** a fully autonomous repair controller. This kit does not automatically commit, push, deploy, write to databases, or use third-party credentials on behalf of other projects.

## Community and support

[Contributing](CONTRIBUTING.md) · [Code of Conduct](CODE_OF_CONDUCT.md) · [Security](SECURITY.md) · [Support](SUPPORT.md) · [Citation](CITATION.cff)
