#!/usr/bin/env python3
"""Run portable-kit self checks without touching a host project."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT)
raise SystemExit(result.returncode)
