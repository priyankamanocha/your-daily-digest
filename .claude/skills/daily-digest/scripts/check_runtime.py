"""
Runtime dependency check for daily-digest skill.

Checks:
  - Python version >= 3.8
  - digests/ directory is writable (creates it if missing)

MCP tool availability (web_search, fetch) cannot be verified from Python —
those checks are noted in the skill as a manual preflight step.

Exit codes:
  0  all checks passed
  1  one or more checks failed
"""

import sys
import os
import json
from pathlib import Path


def check_python_version():
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        return False, f"Python >= 3.8 required, found {major}.{minor}"
    return True, f"Python {major}.{minor} ok"


def check_digests_writable():
    digests_dir = Path("digests")
    try:
        digests_dir.mkdir(parents=True, exist_ok=True)
        probe = digests_dir / ".write_probe"
        probe.write_text("probe")
        probe.unlink()
        return True, "digests/ writable"
    except OSError as e:
        return False, f"digests/ not writable: {e}"


def main():
    checks = [
        check_python_version(),
        check_digests_writable(),
    ]

    results = []
    all_passed = True
    for passed, message in checks:
        results.append({"ok": passed, "message": message})
        if not passed:
            all_passed = False

    print(json.dumps({"passed": all_passed, "checks": results}, indent=2))
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
