"""
Parity test harness.

Captures batch-pipeline and runtime-pipeline behavior as JSON snapshots,
diffable against a committed baseline (see capture_baseline.py). As of
Phase 8, the legacy hand-written parsers/renderers/runtime classes this
harness originally targeted have been deleted; capture_batch() now
defaults to the schema-driven generic engine. The frozen "legacy" baseline
(tests/parity/baseline/legacy.json, captured in Phase 0) remains as the
historical record of pre-migration behavior, bugs included - it cannot be
re-captured since the code it recorded no longer exists.
"""

import json
from pathlib import Path

from configbridge.models.device_inventory import DeviceInventory, DiscoveredInterface
from configbridge.schema.loader import SchemaLoader
from configbridge.engine.generic_parser import GenericConfigParser
from configbridge.engine.generic_generator import GenericConfigGenerator
from configbridge.runtime.runtime_engine import RuntimeEngine

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CONFIGS_DIR = Path(__file__).parent.parent.parent / "sample-configs"
BASELINE_DIR = Path(__file__).parent / "baseline"

RUNTIME_COMMAND_SCRIPT = [
    "configure terminal",
    "interface GigabitEthernet0/0/1",
    "description Uplink to Distribution",
    "switchport mode trunk",
    "shutdown",
    "no shutdown",
    "exit",
    "interface GigabitEthernet0/0/2",
    "switchport mode access",
    "switchport access vlan 10",
    "end",
    "show interfaces status",
    "show vlan brief",
    "show version",
    "write memory",
]


def _batch_fixture_paths():
    """Yield (vendor, name, path) for every batch config fixture."""

    for vendor, root in (("cisco", SAMPLE_CONFIGS_DIR / "cisco"), ("juniper", SAMPLE_CONFIGS_DIR / "juniper")):
        for path in sorted(root.glob("*.txt")):
            if path.name == "show_interfaces_terse.txt":
                continue
            yield vendor, f"sample-configs/{vendor}/{path.name}", path

    for vendor, root in (("cisco", FIXTURES_DIR / "cisco"), ("juniper", FIXTURES_DIR / "juniper")):
        for path in sorted(root.glob("*.txt")):
            yield vendor, f"parity-fixtures/{vendor}/{path.name}", path


def capture_batch(cisco_parser=None, juniper_parser=None, cisco_generator=None, juniper_generator=None):
    """
    Parse every batch fixture with its own vendor's parser, then render the
    resulting Intent Model with BOTH generators (same-vendor round trip and
    cross-vendor transpile), capturing the Intent Model dict and both
    rendered outputs.
    """

    loader = SchemaLoader()
    cisco_parser = cisco_parser or GenericConfigParser(loader.load("cisco_ios"))
    juniper_parser = juniper_parser or GenericConfigParser(loader.load("juniper_junos"))
    cisco_generator = cisco_generator or GenericConfigGenerator(loader.load("cisco_ios"))
    juniper_generator = juniper_generator or GenericConfigGenerator(loader.load("juniper_junos"))

    results = {}

    for vendor, key, path in _batch_fixture_paths():
        config_text = path.read_text()
        parser = cisco_parser if vendor == "cisco" else juniper_parser

        intent = parser.parse(config_text)

        results[key] = {
            "source_vendor": vendor,
            "intent": intent.to_dict(),
            "cisco_render": cisco_generator.generate(intent),
            "juniper_render": juniper_generator.generate(intent),
        }

    return results


def _runtime_inventory():
    return DeviceInventory(
        hostname="CORE-SW1",
        vendor="Juniper Junos",
        interfaces=[
            DiscoveredInterface(name="ge-0/0/1", aliases=["GigabitEthernet0/0/1"]),
            DiscoveredInterface(name="ge-0/0/2", aliases=["GigabitEthernet0/0/2"]),
        ],
    )


def capture_translate_steps(parser, generator):
    """
    Drive the translate() loop (RuntimeEngine.translate()'s own logic,
    reimplemented here so it can run against either the legacy
    RuntimeParser/RuntimeGenerator or the generic schema-driven
    equivalents without modifying runtime/runtime_engine.py, which stays
    untouched until Phase 6's cutover) through the same representative
    command script used by capture_runtime() below.
    """

    generator.set_inventory(_runtime_inventory())

    steps = []

    for command in RUNTIME_COMMAND_SCRIPT:
        runtime_command = parser.parse(command)

        if runtime_command is None:
            translated = command
        else:
            translated = generator.generate(runtime_command)
            if runtime_command.mode_change:
                parser.set_mode(runtime_command.mode_change)

        steps.append(
            {
                "input": command,
                "translated": translated,
                "mode_after": parser.mode,
            }
        )

    return steps


def capture_runtime():
    """
    Drive RuntimeEngine.translate() through a representative command script
    (mode transitions, interface entry/description/switchport, show
    commands, unrecognized-command passthrough), and RuntimeEngine.
    virtualize_output() against a real device output sample.
    """

    engine = RuntimeEngine()
    engine.set_inventory(_runtime_inventory())

    steps = []

    for command in RUNTIME_COMMAND_SCRIPT:
        translated = engine.translate(command)
        steps.append(
            {
                "input": command,
                "translated": translated,
                "mode_after": engine.parser.mode,
            }
        )

    device_output = (SAMPLE_CONFIGS_DIR / "juniper" / "show_interfaces_terse.txt").read_text()
    virtualized = engine.virtualize_output(device_output)

    return {
        "translate_steps": steps,
        "virtualize_output": virtualized,
    }


def capture_all(**kwargs):
    return {
        "batch": capture_batch(**kwargs),
        "runtime": capture_runtime(),
    }


def load_baseline(name: str) -> dict:
    return json.loads((BASELINE_DIR / f"{name}.json").read_text())


def save_baseline(name: str, data: dict) -> None:
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    (BASELINE_DIR / f"{name}.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def diff(baseline: dict, current: dict, path: str = "") -> list[str]:
    """Return a list of human-readable differences between two JSON-like structures."""

    diffs = []

    if isinstance(baseline, dict) and isinstance(current, dict):
        for key in sorted(set(baseline) | set(current)):
            child_path = f"{path}.{key}" if path else key
            if key not in current:
                diffs.append(f"MISSING in current: {child_path}")
            elif key not in baseline:
                diffs.append(f"UNEXPECTED in current: {child_path}")
            else:
                diffs.extend(diff(baseline[key], current[key], child_path))
    elif isinstance(baseline, list) and isinstance(current, list):
        if len(baseline) != len(current):
            diffs.append(f"LENGTH MISMATCH at {path}: baseline={len(baseline)} current={len(current)}")
        for index, (b_item, c_item) in enumerate(zip(baseline, current)):
            diffs.extend(diff(b_item, c_item, f"{path}[{index}]"))
    else:
        if baseline != current:
            diffs.append(f"VALUE MISMATCH at {path}: baseline={baseline!r} current={current!r}")

    return diffs
