import os
import re
import csv
import json
import zipfile
import random
from typing import Any, Dict, List, Optional

from src.generator import DataGenerator
from faker import Faker

fake = Faker()

class InstructionEngine:
    """
    Engine que recibe instrucciones en texto, controla parámetros de generación,
    ejecuta DataGenerator y aplica overrides/postprocesado a los datos generados.
    """

    def __init__(self, schema: Dict[str, Any], generator_cls=DataGenerator):
        self.schema = schema
        self.generator_cls = generator_cls
        self.params = {
            "num_rows": 5,
            "temperature": 1.0,  # placeholder si integrás LLM después
        }
        # overrides: { "TableName": { "column_name": strategy_dict } }
        # strategy_dict: {"type": "fixed"|"list"|"faker"|"range", "value": ...}
        self.overrides: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.generated_data: Dict[str, List[Dict[str, Any]]] = {}
        self.history: List[Dict[str, Any]] = []  # historial simple de instrucciones/resultados

    # ----------------------
    # Public API
    # ----------------------
    def set_param(self, key: str, value: Any) -> None:
        self.params[key] = value

    def add_override(self, table: str, column: str, strategy: Dict[str, Any]) -> None:
        if table not in self.schema["tables"]:
            raise ValueError(f"Tabla desconocida: {table}")

        if column not in self.schema["tables"][table]["columns"]:
            raise ValueError(f"Columna desconocida: {table}.{column}")

        self.overrides.setdefault(table, {})[column] = strategy

    def remove_override(self, table: str, column: str) -> None:
        if table in self.overrides and column in self.overrides[table]:
            del self.overrides[table][column]

    def clear_overrides(self) -> None:
        self.overrides = {}

    def generate(self, num_rows: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Llama al DataGenerator y luego aplica overrides sobre el resultado."""
        if num_rows is None:
            num_rows = self.params.get("num_rows", 5)
        # Construir generator con schema actual
        generator = self.generator_cls(self.schema)
        data = generator.generate(num_rows=num_rows)
        self.generated_data = data
        # Aplicar overrides post-generación (manteniendo integridad FK)
        self._apply_all_overrides()
        # Guardar snapshot en historial
        self.history.append({
            "action": "generate",
            "num_rows": num_rows,
            "overrides": json.loads(json.dumps(self.overrides)),  # copy serializable
            "result_counts": {t: len(rows) for t, rows in self.generated_data.items()},
        })
        return self.generated_data

    def parse_and_apply_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Parsea instrucciones simples y las aplica.
        Devuelve un dict con keys: 'ok':bool, 'message':str, 'result': optional data
        Soporta:
          - "generate N rows" / "genera N filas"
          - "set TABLE.COLUMN to VALUE" / "para TABLE, columna COLUMN usar X"
          - "set TABLE.COLUMN from list a,b,c"
          - "set TABLE.COLUMN faker city"  (usar provider faker)
          - "clear overrides"
          - "download csv"
        """
        raw = instruction.strip()
        text = raw.lower()

        # GENERATE N ROWS
        m = re.search(r"(generate|genera)\s+(\d+)\s+(rows|filas)?", text)
        if m:
            n = int(m.group(2))
            self.set_param("num_rows", n)
            data = self.generate(num_rows=n)
            return {"ok": True, "message": f"Generadas {n} filas por tabla.", "result": data}

        # SET FROM LIST: "set Companies.industry from list Tech,Finance,Health"
        m = re.search(r"set\s+([\w\d_]+)\.([\w\d_]+)\s+from\s+list\s+(.+)", raw, re.IGNORECASE)
        if m:
            table, column, rest = m.group(1), m.group(2), m.group(3)
            # split by comma
            choices = [c.strip() for c in re.split(r",\s*", rest) if c.strip()]
            self.add_override(table, column, {"type": "list", "value": choices})
            return {"ok": True, "message": f"Override agregado: {table}.{column} a partir de lista {choices}"}

        # SET FIXED: "set Companies.country to Argentina"
        m = re.search(r"set\s+([\w\d_]+)\.([\w\d_]+)\s+to\s+(.+)", text)
        if m:
            table, column, rest = m.group(1), m.group(2), m.group(3)
            val = rest.strip()
            # si lista con comas se interpreta como list
            if "," in val:
                choices = [c.strip() for c in val.split(",") if c.strip()]
                self.add_override(table, column, {"type": "list", "value": choices})
                return {"ok": True, "message": f"Override agregado: {table}.{column} lista {choices}"}
            # si es faker provider: faker:city() o faker.city()
            faker_match = re.match(r"(faker[:\.])?([\w_]+)\s*\(?\)?", val)
            if faker_match and faker_match.group(2) in _FAKER_SHORTMAP:
                provider = _FAKER_SHORTMAP[faker_match.group(2)]
                self.add_override(table, column, {"type": "faker", "value": provider})
                return {"ok": True, "message": f"Override agregado: {table}.{column} -> faker provider {provider}"}
            # value literal
            self.add_override(table, column, {"type": "fixed", "value": val})
            return {"ok": True, "message": f"Override agregado: {table}.{column} -> '{val}'"}

        # SET FAKER: "set Companies.website faker url" or "set Companies.city faker city"
        m = re.search(r"set\s+([\w\d_]+)\.([\w\d_]+)\s+faker\s+([\w_]+)", text)
        if m:
            table, column, prov = m.group(1), m.group(2), m.group(3)
            if prov in _FAKER_SHORTMAP:
                self.add_override(table, column, {"type": "faker", "value": _FAKER_SHORTMAP[prov]})
                return {"ok": True, "message": f"Override faker agregado: {table}.{column} -> {prov}"}
            return {"ok": False, "message": f"Provider faker desconocido: {prov}"}

        # CLEAR OVERRIDES
        if "clear overrides" in text or "borrar overrides" in text or "limpiar overrides" in text:
            self.clear_overrides()
            return {"ok": True, "message": "Overrides limpiados."}

        # GENERATE & DOWNLOAD (quick)
        if "download csv" in text or "descargar csv" in text or "download zip" in text:
            # asegúrate de generar si no está generado
            if not self.generated_data:
                self.generate(num_rows=self.params.get("num_rows", 5))
            zip_path = self.save_all_as_csv_zip()
            return {"ok": True, "message": f"CSV(s) guardados en {zip_path}", "path": zip_path}

        return {"ok": False, "message": "Instrucción no reconocida. Prueba: 'generate 100 rows' o 'set Companies.industry from list Tech,Finance'."}

    def get_preview(self, table: str, n: int = 5) -> List[Dict[str, Any]]:
        rows = self.generated_data.get(table, [])[:n]
        return rows

    # ----------------------
    # Persistence / export helpers
    # ----------------------
    def save_table_csv(self, table: str, output_path: str) -> str:
        rows = self.generated_data.get(table)
        if rows is None:
            raise ValueError("No hay datos generados para la tabla: " + table)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return output_path

    def save_all_as_csv_zip(self, folder: str = "generated_csv", zip_name: str = "generated_data.zip") -> str:
        """Guarda cada tabla como CSV y los comprime en zip. Devuelve la ruta del zip."""
        os.makedirs(folder, exist_ok=True)
        csv_paths = []
        for table, rows in self.generated_data.items():
            if not rows:
                continue
            path = os.path.join(folder, f"{table}.csv")
            self.save_table_csv(table, path)
            csv_paths.append(path)

        zip_path = os.path.join(folder, zip_name)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in csv_paths:
                zf.write(p, arcname=os.path.basename(p))
        return zip_path

    # ----------------------
    # Internals: applying overrides
    # ----------------------
    def _apply_all_overrides(self) -> None:
        """Itera por overrides y aplica por tabla/columna."""
        for table, cols in self.overrides.items():
            if table not in self.generated_data:
                continue
            for col, strat in cols.items():
                self._apply_override_to_table_column(table, col, strat)

    def _apply_override_to_table_column(self, table: str, column: str, strat: Dict[str, Any]) -> None:
        rows = self.generated_data.get(table, [])
        if not rows:
            return

        t = strat.get("type")
        v = strat.get("value")

        if t == "fixed":
            for r in rows:
                r[column] = v
            return

        if t == "list":
            choices = v if isinstance(v, list) else [v]
            for r in rows:
                r[column] = random.choice(choices)
            return

        if t == "faker":
            provider = v  # string name of faker provider or callable
            for r in rows:
                r[column] = _call_faker_provider(provider)
            return

        if t == "range":
            # value expected to be tuple (min, max)
            mn, mx = v
            for r in rows:
                r[column] = random.randint(mn, mx)
            return

        # unknown -> no-op
        return

# ----------------------
# Helper utilities
# ----------------------
# Map short faker names to actual provider names or lambdas
_FAKER_SHORTMAP = {
    "city": "city",
    "state": "state",
    "company": "company",
    "job": "job",
    "url": "url",
    "email": "email",
    "first_name": "first_name",
    "last_name": "last_name",
    "phone": "phone_number",
    "address": "address",
    "zip": "zipcode",
}

def _call_faker_provider(provider: str):
    """Llama al provider de faker por nombre y devuelve valor."""
    if not provider:
        return None
    # manejar providers simples
    if hasattr(fake, provider):
        attr = getattr(fake, provider)
        if callable(attr):
            try:
                return attr()
            except TypeError:
                # algún provider puede requerir args; fallback a string
                return str(attr)
        return attr
    # fallback
    return None
