"""
Runtime CLI engine.
"""

from configbridge.runtime.runtime_parser import RuntimeParser
from configbridge.runtime.runtime_generator import RuntimeGenerator


class RuntimeEngine:

    def __init__(self):

        self.parser = RuntimeParser()

        self.generator = RuntimeGenerator()

    def translate(self, command: str) -> str:

        runtime = self.parser.parse(command)

        if runtime is None:
            return command

        return self.generator.generate(runtime)