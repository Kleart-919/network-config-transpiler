from configbridge.runtime.runtime_engine import RuntimeEngine

engine = RuntimeEngine()

commands = [

    "show version",

    "show interfaces status",

    "show vlan brief",

    "show ip interface brief",

]

for command in commands:

    print()

    print(command)

    print("↓")

    print(engine.translate(command))