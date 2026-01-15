import os
import sys
import json
import pytest

# Asegurar acceso al paquete src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generator import DataGenerator

@pytest.fixture
def schema():
    with open("schema_output.json", "r", encoding="utf-8") as f:
        return json.load(f)

def test_generate_data(schema):
    generator = DataGenerator(schema)
    data = generator.generate(num_rows=3)

    output_path = "generated_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\n💾 Datos generados guardados en: {output_path}")

    assert isinstance(data, dict)
    assert "Companies" in data
    assert all(isinstance(row, dict) for row in data["Companies"])

    # Verificar que todas las tablas del esquema estén generadas
    assert set(schema["tables"].keys()) == set(data.keys())

    # Verificar algunas columnas de ejemplo
    company = data["Companies"][0]
    assert "name" in company
    assert isinstance(company["name"], str)
    assert "company_id" in company
    assert isinstance(company["company_id"], int)

    # Verificar integridad general (no vacío)
    for table_name, rows in data.items():
        assert len(rows) == 3
        for row in rows:
            assert isinstance(row, dict)