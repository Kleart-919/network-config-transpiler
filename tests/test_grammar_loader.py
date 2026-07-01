from configbridge.runtime.grammar.grammar_loader import GrammarLoader

loader = GrammarLoader()

grammar = loader.load("Cisco IOS")

print(grammar["vendor"])

print()

print(grammar["modes"]["exec"]["commands"].keys())