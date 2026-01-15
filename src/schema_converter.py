import json
from typing import List, Dict, Any
from .ddl_parser import Table

def normalize_type(raw_type: str) -> str:
    """
    Limpia y normaliza los tipos de datos SQL.
    """
    t = raw_type.strip().upper()
    # Elimina espacios duplicados
    t = " ".join(t.split())
    return t

def table_to_dict(table: Table) -> Dict[str, Any]:
    """
    Convierte un objeto Table en un diccionario serializable (JSON-ready).
    """
    columns_dict = {}
    for col in table.columns:
        columns_dict[col.name] = {
            "type": normalize_type(col.raw_type),
            "not_null": col.not_null,
            "default": col.default,
            "primary_key": col.is_primary or col.name in table.primary_keys,
            "unique": col.is_unique,
            "auto_increment": getattr(col, "auto_increment", False),
            "check": getattr(col, "check", None)
        }

    fks = []
    for fk in table.foreign_keys:
        fks.append({
            "columns": fk.cols,
            "ref_table": fk.ref_table,
            "ref_columns": fk.ref_cols
        })

    return {
        "name": table.name,
        "columns": columns_dict,
        "primary_keys": table.primary_keys,
        "foreign_keys": fks,
    }

def schema_to_dict(tables: List[Table]) -> Dict[str, Any]:
    """
    Convierte toda la lista de tablas en un esquema JSON completo.
    """
    schema = {
        "tables": {t.name: table_to_dict(t) for t in tables},
        "meta": {
            "version": 1,
            "generator": "ddl_parser",
        }
    }
    return schema

def schema_to_json(tables: List[Table], indent: int = 2) -> str:
    """
    Devuelve un string JSON bien formateado del esquema.
    """
    return json.dumps(schema_to_dict(tables), indent=indent)

def save_schema_json(tables: List[Table], output_path: str = "schema_output.json", indent: int = 2) -> None:
    """
    Convierte la lista de tablas a JSON y la guarda en un archivo.
    """
    schema_dict = schema_to_dict(tables)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema_dict, f, indent=indent, ensure_ascii=False)
    print(f"✅ Esquema guardado en {output_path}")

