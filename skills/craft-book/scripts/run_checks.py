#!/usr/bin/env python3
"""Run the book's numeric spot-checks.

    run_checks.py checks/

Every checkpoint or worked example with a number in it gets a small Python file
in checks/ that recomputes the number and asserts it. This catches the class of
error where the prose is fluent and the arithmetic is wrong. Files run in name
order; any exception fails the build.
"""

from __future__ import annotations

import pathlib
import runpy
import sys


def main(directory: str) -> None:
    files = sorted(pathlib.Path(directory).glob("*.py"))
    if not files:
        print("numeric checks: none found (add checks/NN-topic.py with assertions)")
        return
    for path in files:
        try:
            runpy.run_path(str(path), run_name="__main__")
        except Exception as error:  # noqa: BLE001 - report and fail
            raise SystemExit(f"numeric check failed in {path.name}: {error!r}")
        print(f"ok  {path.name}")
    print(f"numeric checks: {len(files)} passed")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "checks")
