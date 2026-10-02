# Universal Codex Kaizen · Wenjin · Shell Gate Kit

[繁體中文](README.md)

The name uses `universal` for portability, `kaizen-wenjin` for the method, and `shell-kit` for the deliverable. The GitHub repository uses lowercase words separated by hyphens for readability and easy typing.

A portable engineering toolkit for making small verifiable changes, preserving existing behavior, and collecting real command-execution evidence.

## What it provides

1. **Kaizen** — make one small, verifiable change at a time.
2. **Wenjin** — inspect the current state, define preserved behavior and verification scope, then change; new work must not silently break already-passed flows.
3. **Shell Gate** — execute real commands and record exit codes, output, timestamps, risk classification, and evidence instead of treating model text as proof of success.

## What it does not provide

This kit is not a complete autonomous repair controller. Wenjin is currently a delivery/governance protocol implemented through documented rules and verification steps; it does not independently decide rollback, repair, or progression for every project.

It does not automatically commit, push, deploy, modify databases, or use third-party credentials.

## Installation

1. Extract the archive safely.
2. Merge the `AGENTS.md` delivery-gate section into an existing project `AGENTS.md`; do **not** overwrite existing project instructions.
3. Copy `scripts/shell_gate.py` into the target project, for example `.codex/tools/shell_gate.py`.
4. Run:

```bash
python3 .codex/tools/shell_gate.py doctor --cwd .
python3 .codex/tools/shell_gate.py project-check --cwd .
```

See [`docs/USAGE.md`](docs/USAGE.md) for the complete installation and usage guide.

**Want to give the ZIP to Codex?** Download it, attach it to a Codex conversation, and open the target project there. Then use the [copy-ready prompt in the usage guide](docs/USAGE.md#give-the-zip-to-codex) to explicitly request installation. Attaching the ZIP alone does not guarantee that your project will be modified.

## Verification

Run the included tests:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_kit.py
```

A `PASS` means that the corresponding command produced traceable execution evidence. It does not by itself mean that a production deployment is safe or ready.

## Security

Do not commit API keys, OAuth secrets, tokens, passwords, private keys, customer data, database credentials, or deployment credentials.

See `SECURITY.md` for reporting security issues.

## License

The project is licensed under the MIT License. See `LICENSE`.

MIT permits commercial use, modification, distribution, private use, and sublicensing, subject to the license conditions and disclaimer.

## Repository language

- 繁體中文：`README.md`
- English: `README.en.md`
