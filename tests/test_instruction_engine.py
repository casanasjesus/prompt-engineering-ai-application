import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ddl_parser import parse_ddl_file
from src.schema_converter import schema_to_dict
from src.instruction_engine import InstructionEngine

def test_engine_basic():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ddl_path = os.path.join(base_dir, "src", "ddl", "company_employee_schema.ddl")

    tables = parse_ddl_file(ddl_path)
    schema = schema_to_dict(tables)

    engine = InstructionEngine(schema)

    # Test #1: Generate
    engine.parse_and_apply_instruction("generate 3 rows")
    data = engine.generated_data

    assert "Companies" in data
    assert len(data["Companies"]) == 3

    # Test #2: Overrides desde lista
    engine.parse_and_apply_instruction("set Companies.industry from list Tech,Finance")
    engine.parse_and_apply_instruction("generate 3 rows")

    vals = {r["industry"] for r in engine.generated_data["Companies"]}
    assert vals.issubset({"Tech", "Finance"})
