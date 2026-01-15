import os
import sys

# 1️⃣ Determinar el directorio raíz del proyecto
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2️⃣ Agregar la carpeta src al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 3️⃣ Ahora sí importar
from src.ddl_parser import parse_ddl_file, tables_dependency_order
from src.schema_converter import schema_to_json, save_schema_json

ddl_path = os.path.join(base_dir, "src", "ddl", "company_employee_schema.ddl")
output_path = os.path.join(base_dir, "schema_output.json")

def test_schema_conversion():
    """Testea la conversión del DDL a JSON y genera el archivo."""
    tables = parse_ddl_file(ddl_path)
    assert isinstance(tables, list)
    assert len(tables) > 0

    json_schema = schema_to_json(tables)
    assert isinstance(json_schema, str)

    parsed = __import__("json").loads(json_schema)
    assert "tables" in parsed

    save_schema_json(tables, output_path)
    assert os.path.exists(output_path)

# Permite ejecutarlo manualmente también
if __name__ == "__main__":
    tables = parse_ddl_file(ddl_path)
    print("✅ Orden sugerido:", tables_dependency_order(tables))
    print("\n✅ Esquema JSON:\n", schema_to_json(tables))
    save_schema_json(tables, output_path)
    print(f"\n💾 Archivo guardado en: {output_path}")
