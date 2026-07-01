"""
Grammar-based runtime parser.
"""

from configbridge.runtime.grammar.grammar_loader import (
    GrammarLoader,
)
from configbridge.runtime.runtime_command import RuntimeCommand


class RuntimeParser:

    def __init__(self):

        self.loader = GrammarLoader()

        self.grammar = self.loader.load(
            "Cisco IOS"
        )

        self.mode = "exec"

    def parse(
        self,
        command: str,
    ) -> RuntimeCommand | None:

        tokens = command.strip().split()

        if not tokens:
            return None

        node = self.grammar["modes"][self.mode]["commands"]

        runtime = None

        consumed = []

        for token in tokens:

            key = self.expand_token(
                token,
                node,
            )

            if key is None:
                break

            consumed.append(key)

            node = node[key]

            if "runtime" in node:
                runtime = node["runtime"]

            if "children" in node:
                node = node["children"]

        if runtime is None:
            return None

        parts = runtime.split(".")

        return RuntimeCommand(

            verb=parts[0],

            resource=parts[1],

            qualifier=parts[2] if len(parts) > 2 else None,

            arguments=tokens[len(consumed):],

        )

    def expand_token(
        self,
        token,
        node,
    ):

        token = token.lower()

        matches = []

        for command in node:

            minimum = node[command]["minimum"]

            if (
                command.startswith(token)
                and len(token) >= len(minimum)
            ):
                matches.append(command)

        if len(matches) != 1:
            return None

        return matches[0]