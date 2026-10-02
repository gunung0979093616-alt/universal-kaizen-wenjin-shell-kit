#!/usr/bin/env python3
"""Portable, evidence-first command runner for Codex projects.

It deliberately accepts argv after ``--`` and never invokes a command shell.
The runner is not an authorization system: it blocks obvious destructive
commands and records every invocation, while each host project keeps control
of its own approval, secrets, deployment and database policies.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


STATES = {
    "NOT_STARTED", "RUNNING", "SUCCESS", "FAILED", "BLOCKED", "REPAIRING", "RETRYING", "VERIFIED"
}
SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s\"']+"),
    re.compile(r"(?i)((?:api[_-]?key|secret|password|token)\s*[:=]\s*)[^\s\"']+"),
    re.compile(r"\b(sk-[A-Za-z0-9_-]{12,})\b"),
)
# Verification logs prove this build outside the deliverable.  Excluding them
# also prevents a ZIP command from packaging the evidence file being written by
# its own invocation.
EXCLUDED_ZIP_NAMES = {".git", ".venv", "venv", "node_modules", ".codex-shell-evidence", "__pycache__", "evidence"}
EXCLUDED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".keystore", ".jks"}
SECRET_NAME_RE = re.compile(
    r"(?i)(^\.env(?:\.|$)|credentials?|secrets?|service[-_]?account|"
    r"id_(?:rsa|dsa|ecdsa|ed25519)|\.npmrc$|\.pypirc$|\.netrc$|"
    r"auth(?:entication)?|private[-_]?key)"
)
SECRET_CONTENT_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=:-]{12,}"),
    re.compile(rb"\bsk-[A-Za-z0-9_-]{12,}\b"),
)
# Commands known to be observational. Everything else defaults to write-risk.
READ_ONLY_COMMANDS = {
    "cat", "head", "tail", "grep", "egrep", "fgrep", "rg", "find", "ls", "pwd",
    "wc", "stat", "file", "which", "whereis", "env", "printenv", "echo", "printf",
    "uname", "whoami", "id", "date", "true", "false",
}
READ_ONLY_GIT = {"status", "diff", "log", "show", "branch", "rev-parse", "remote", "ls-files", "tag"}
READ_ONLY_PYTHON_MODULES = {"pytest", "unittest", "compileall"}
READ_ONLY_NPM_ACTIONS = {"test", "run", "list", "ls", "view", "info", "why", "outdated"}


@dataclass
class CommandEvidence:
    command: list[str]
    working_directory: str
    started_at: str
    finished_at: str
    exit_code: int | None
    stdout: str
    stderr: str
    result: str
    state: str
    risk: str
    evidence: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize(value: str, limit: int = 20000) -> str:
    value = value[-limit:]
    for pattern in SECRET_PATTERNS:
        value = pattern.sub(lambda match: f"{match.group(1) if match.lastindex else ''}[REDACTED]", value)
    return value


def resolve_root(cwd: str) -> Path:
    root = Path(cwd).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"工作目錄不存在：{root}")
    return root


def classify(argv: list[str]) -> tuple[str, str | None]:
    """Conservative policy: known observation commands are read-only; unknowns require write approval."""
    if not argv:
        return "write", None
    cmd = Path(argv[0]).name.lower()
    args = [part.lower() for part in argv[1:]]

    if cmd == "rm" and any(a in {"-rf", "-fr"} or (a.startswith("-") and "r" in a and "f" in a) for a in args):
        return "high", "拒絕高風險命令：rm recursive force"
    if cmd == "git" and args:
        action = args[0]
        if action == "push":
            return "high", "拒絕直接推送；請使用目標專案自己的明確授權流程"
        if action == "reset" and "--hard" in args[1:]:
            return "high", "拒絕高風險命令：git reset --hard"
        if action == "clean" and any("f" in a for a in args[1:] if a.startswith("-")):
            return "high", "拒絕高風險命令：git clean force"
        if action in READ_ONLY_GIT:
            return "read_only", None
        return "write", None

    if cmd in {"sqlite3", "psql", "mysql", "mariadb"}:
        sql = " ".join(args)
        if re.search(r"\b(drop\s+(?:database|table)|truncate\s+table)\b", sql, re.I):
            return "high", "拒絕破壞性資料庫命令"
        # Database clients can mutate even when mutation is not obvious.
        return "write", None

    if cmd in {"deploy", "render", "vercel", "flyctl"}:
        return "high", "部署必須使用專案自己的明確授權流程"

    if cmd in READ_ONLY_COMMANDS:
        return "read_only", None

    if cmd == "git":
        return "read_only", None

    if cmd.startswith("python"):
        if "-m" in args:
            try:
                module = args[args.index("-m") + 1]
            except (ValueError, IndexError):
                module = ""
            if module in READ_ONLY_PYTHON_MODULES:
                return "read_only", None
        # Scripts and inline code are Turing-complete and can write.
        return "write", None

    if cmd in {"pytest", "py.test"}:
        return "read_only", None

    if cmd in {"npm", "pnpm", "yarn"}:
        action = args[0] if args else ""
        if action in READ_ONLY_NPM_ACTIONS:
            return "read_only", None
        return "write", None

    # Shells, interpreters, cp/mv/sed and every unknown executable are write-risk
    # by default. This closes wrapper/interpreter bypasses without pretending to
    # be an OS sandbox.
    return "write", None


def evidence_dir(root: Path) -> Path:
    path = root / ".codex-shell-evidence"
    path.mkdir(exist_ok=True)
    return path


def persist(root: Path, record: CommandEvidence) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = evidence_dir(root) / f"{stamp}.json"
    path.write_text(json.dumps(asdict(record), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def run_argv(root: Path, argv: list[str], timeout: float = 120.0, allow_write: bool = False) -> tuple[CommandEvidence, Path]:
    if not argv:
        raise ValueError("請在 -- 後提供 argv 命令")
    risk, blocked_reason = classify(argv)
    started = utc_now()
    if blocked_reason or (risk == "write" and not allow_write):
        reason = blocked_reason or "此命令可能修改檔案或 Git；需加 --allow-write 並遵守目標專案授權流程"
        record = CommandEvidence(argv, str(root), started, utc_now(), None, "", reason, "FAILED", "BLOCKED", risk, reason)
        return record, persist(root, record)
    try:
        completed = subprocess.run(argv, cwd=root, text=True, capture_output=True, timeout=timeout, check=False, shell=False)
        result = "SUCCESS" if completed.returncode == 0 else "FAILED"
        state = "VERIFIED" if completed.returncode == 0 else "FAILED"
        detail = "退出碼為 0" if completed.returncode == 0 else f"退出碼為 {completed.returncode}"
        record = CommandEvidence(argv, str(root), started, utc_now(), completed.returncode, sanitize(completed.stdout), sanitize(completed.stderr), result, state, risk, detail)
    except subprocess.TimeoutExpired as error:
        record = CommandEvidence(argv, str(root), started, utc_now(), None, sanitize(error.stdout or ""), sanitize(error.stderr or ""), "FAILED", "FAILED", risk, f"逾時：{timeout} 秒")
    except OSError as error:
        record = CommandEvidence(argv, str(root), started, utc_now(), None, "", sanitize(str(error)), "FAILED", "FAILED", risk, "命令無法啟動")
    return record, persist(root, record)


def git_value(root: Path, *args: str) -> str | None:
    if not shutil.which("git"):
        return None
    done = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return done.stdout.strip() if done.returncode == 0 else None


def doctor(root: Path) -> dict[str, object]:
    managers = {name: shutil.which(name) is not None for name in ("git", "python3", "pip", "npm", "pnpm", "yarn", "uv", "poetry")}
    return {
        "state": "VERIFIED",
        "working_directory": str(root),
        "operating_system": platform.platform(),
        "python": sys.version.split()[0],
        "tools": managers,
        "git_branch": git_value(root, "branch", "--show-current"),
        "git_commit": git_value(root, "rev-parse", "HEAD"),
        "git_status": git_value(root, "status", "--short"),
    }


def project_check(root: Path) -> dict[str, object]:
    names = {entry.name for entry in root.iterdir()}
    config = sorted(names & {"pyproject.toml", "package.json", "Cargo.toml", "go.mod", "requirements.txt", "Pipfile", "poetry.lock", "uv.lock"})
    builds = sorted(names & {"Makefile", "Dockerfile", "render.yaml", "vite.config.ts", "next.config.js"})
    test_dirs = sorted(entry.name for entry in root.iterdir() if entry.is_dir() and entry.name in {"test", "tests", "__tests__", "spec"})
    env_files = sorted(name for name in names if name in {".env.example", ".env.sample", ".env.template"})
    return {
        "state": "VERIFIED",
        "project_exists": True,
        "project_name": root.name,
        "dependency_or_runtime_files": config,
        "build_files": builds,
        "test_directories": test_dirs,
        "environment_templates": env_files,
        "git": {"branch": git_value(root, "branch", "--show-current"), "commit": git_value(root, "rev-parse", "HEAD")},
    }


def should_archive(relative: Path) -> bool:
    if any(part in EXCLUDED_ZIP_NAMES for part in relative.parts):
        return False
    lower_name = relative.name.lower()
    if SECRET_NAME_RE.search(lower_name) or relative.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return True


def contains_secret_content(source: Path, max_scan_bytes: int = 2_000_000) -> bool:
    """Scan likely configuration/data/text files without dropping source files that contain security test fixtures."""
    scannable = {".json", ".yaml", ".yml", ".txt", ".ini", ".cfg", ".conf", ".toml", ".properties"}
    if source.suffix.lower() not in scannable:
        return False
    try:
        if source.stat().st_size > max_scan_bytes:
            return False
        data = source.read_bytes()
    except OSError:
        return True
    return any(pattern.search(data) for pattern in SECRET_CONTENT_PATTERNS)


def make_zip(root: Path, output: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    output = output.expanduser().resolve()
    if output.exists() and output.is_dir():
        raise ValueError("ZIP 輸出位置不能是目錄")
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    skipped_sensitive: list[str] = []
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in root.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(root)
            if source.is_symlink():
                continue
            resolved = source.resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                continue
            if resolved == output or not should_archive(relative):
                if resolved != output:
                    skipped_sensitive.append(relative.as_posix())
                continue
            if contains_secret_content(source):
                skipped_sensitive.append(relative.as_posix())
                continue
            archive.write(source, relative.as_posix())
            count += 1
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        entries = archive.namelist()
    if bad:
        raise RuntimeError(f"ZIP 驗證失敗：{bad}")
    if count == 0:
        raise RuntimeError("ZIP 沒有可交付檔案")
    return {
        "state": "VERIFIED", "output": str(output), "file_count": count,
        "entries": entries[:50], "skipped_sensitive": skipped_sensitive[:100],
        "evidence": "ZIP 可正常開啟、CRC 驗證通過，且已套用敏感檔名/內容與符號連結防護",
    }


def http_check(url: str, timeout: float = 10.0) -> dict[str, object]:
    started = utc_now()
    request = urllib.request.Request(url, headers={"User-Agent": "codex-shell-gate/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            code = response.status
            body = sanitize(response.read(1024).decode("utf-8", errors="replace"))
        return {"state": "VERIFIED" if 200 <= code < 400 else "FAILED", "url": url, "status": code, "body_preview": body, "started_at": started, "finished_at": utc_now()}
    except urllib.error.URLError as error:
        return {"state": "FAILED", "url": url, "error": sanitize(str(error)), "started_at": started, "finished_at": utc_now()}


def print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evidence-first Shell gate; commands must follow -- as argv.")
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("doctor", "project-check"):
        child = sub.add_parser(action)
        child.add_argument("--cwd", default=".")
    run = sub.add_parser("run")
    run.add_argument("--cwd", default=".")
    run.add_argument("--timeout", type=float, default=120.0)
    run.add_argument("--allow-write", action="store_true")
    run.add_argument("command", nargs=argparse.REMAINDER)
    zipped = sub.add_parser("zip")
    zipped.add_argument("--cwd", default=".")
    zipped.add_argument("--output", required=True)
    http = sub.add_parser("http")
    http.add_argument("--url", required=True)
    http.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.action in {"doctor", "project-check"}:
        result = doctor(resolve_root(args.cwd)) if args.action == "doctor" else project_check(resolve_root(args.cwd))
        print_json(result)
        return 0
    if args.action == "run":
        command = args.command[1:] if args.command and args.command[0] == "--" else args.command
        record, path = run_argv(resolve_root(args.cwd), command, args.timeout, args.allow_write)
        data = asdict(record) | {"evidence_file": str(path)}
        print_json(data)
        return 0 if record.result == "SUCCESS" else 1
    if args.action == "zip":
        print_json(make_zip(resolve_root(args.cwd), Path(args.output)))
        return 0
    if args.action == "http":
        result = http_check(args.url, args.timeout)
        print_json(result)
        return 0 if result["state"] == "VERIFIED" else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
