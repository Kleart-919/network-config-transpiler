"""
Parity gate: re-capture pipeline behavior and diff against the committed
"current" baseline (tests/parity/baseline/current.json) - the go-forward
regression target as of Phase 7, reflecting the deliberate interface-naming
bug fix (see schema/vendors/*.yaml naming_convention comments). The
"legacy" baseline (Phase 0, pre-migration, bugs included) stays as an
immutable historical record - see capture_baseline.py.

Both the batch pipeline (parse + generate, both vendors) and the runtime
pipeline (RuntimeEngine, including output virtualization) run through the
schema-driven generic engine as of Phase 6/7. Zero differences here means
nothing has changed since the last deliberate, reviewed update.

    PYTHONPATH=src python tests/parity/run_parity.py
"""

import sys

from harness import capture_all, diff, load_baseline

if __name__ == "__main__":
    baseline = load_baseline("current")
    current = capture_all()

    differences = diff(baseline, current)

    if differences:
        print(f"PARITY FAILED: {len(differences)} difference(s)\n")
        for line in differences:
            print(f"  {line}")
        sys.exit(1)

    print(f"PARITY OK: {len(current['batch'])} batch fixtures, "
          f"{len(current['runtime']['translate_steps'])} runtime steps, zero differences.")
