"""
Grammar-based runtime parser.
"""

from configbridge.runtime.grammar.grammar_loader import GrammarLoader
from configbridge.runtime.runtime_command import RuntimeCommand


class RuntimeParser:

    def __init__(self):
        self.loader = GrammarLoader()
        self.grammar = self.loader.load("Cisco IOS")
        self.mode = "exec"

    def set_mode(self, mode: str):
        self.mode = mode

    def parse(self, command: str) -> RuntimeCommand | None:
        tokens = command.strip().split()

        if not tokens:
            return None

        node = self.grammar["modes"][self.mode]["commands"]
        runtime = None
        consumed_count = 0

        for token in tokens:
            key = self.expand_token(token, node)

            if key is None:
                break

            consumed_count += 1
            node = node[key]

            if "runtime" in node:
                runtime = node["runtime"]

            if "children" in node:
                node = node["children"]
            else:
                break

        if runtime is None:
            return None

        arguments = tokens[consumed_count:]

        mode_change = None

        if runtime == "configure.terminal":
            mode_change = "config"

        elif runtime == "interface.enter":
            mode_change = "interface"

        elif runtime == "mode.exit":
            mode_change = "config"

        elif runtime == "mode.end":
            mode_change = "exec"

        return RuntimeCommand(
            operation=runtime,
            arguments=arguments,
            mode_change=mode_change,
        )

    def expand_token(self, token, node):
        token = token.lower()
        matches = []

        for command in node:
            command_text = str(command)
            minimum = str(node[command]["minimum"])

            if command_text.startswith(token) and len(token) >= len(minimum):
                matches.append(command_text)

        if len(matches) != 1:
            return None

        return matches[0]