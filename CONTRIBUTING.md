# Contributing

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
