"""
Capture pipeline behavior (schema-driven generic engine) as the committed
"current" parity baseline, re-run whenever a deliberate, reviewed behavior
change is made (e.g. Phase 7's interface-naming bug fix).

    PYTHONPATH=src python tests/parity/capture_baseline.py

tests/parity/baseline/legacy.json is a separate, frozen historical record
captured once in Phase 0 against the original hand-written
parsers/generators/runtime engine (deleted in Phase 8) - it documents
pre-migration behavior, bugs included, and can no longer be re-captured.
"""

from harness import capture_all, save_baseline

if __name__ == "__main__":
    data = capture_all()
    save_baseline("current", data)
    print(f"Captured baseline 'current': {len(data['batch'])} batch fixtures, "
          f"{len(data['runtime']['translate_steps'])} runtime steps.")
    print("Saved to tests/parity/baseline/current.json")
    print(f"Captured baseline '{name}': {len(data['batch'])} batch fixtures, "
          f"{len(data['runtime']['translate_steps'])} runtime steps.")
    print(f"Saved to tests/parity/baseline/{name}.json")
