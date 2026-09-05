"""Known-bad Bandit fixture.

This file must fail Bandit at HIGH (B602 shell=True). Do not add it to
the scoped repository baseline.
"""

from __future__ import annotations

import subprocess


def broken(command: str) -> subprocess.Popen[bytes]:
    return subprocess.Popen(command, shell=True)
