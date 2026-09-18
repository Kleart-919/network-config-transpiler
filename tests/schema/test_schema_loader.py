"""
Loads both committed vendor schema files and prints a structural summary.

Proves the schema files are well-formed against SchemaLoader's validation
before Phase 2/3 build a generic engine against them. Does not exercise any
parsing/rendering logic - the schemas are unwired at this point.

    PYTHONPATH=src python tests/schema/test_schema_loader.py
"""

from configbridge.schema.loader import SchemaLoader

loader = SchemaLoader()

for vendor_id in ("cisco_ios", "juniper_junos"):
    schema = loader.load(vendor_id)

    print(f"=== {schema.display_name} ({schema.vendor_id}) ===")
    print(f"tokenizer style: {schema.tokenizer_style}")
    print(f"naming recognizers: {len(schema.naming.recognizes)}")
    print(f"concepts: {list(schema.concepts.keys())}")
    print(f"has runtime section: {schema.runtime is not None}")
    print()

print("All vendor schemas loaded and validated successfully.")
