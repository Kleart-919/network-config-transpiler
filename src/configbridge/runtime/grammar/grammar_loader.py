"""
Loads vendor CLI grammar files.
"""

from pathlib import Path

import yaml


class GrammarLoader:

    def __init__(self):

        self.base_path = Path(__file__).parent

    def load(self, vendor: str) -> dict:

        filename = (
            vendor.lower()
            .replace(" ", "_")
            .replace("-", "_")
            + ".yaml"
        )

        grammar = self.base_path / filename

        with open(grammar, "r", encoding="utf-8") as file:

            return yaml.safe_load(file)