import random
import re
from faker import Faker

fake = Faker()

class DataGenerator:
    def __init__(self, schema: dict):
        self.schema = schema
        self.generated_data = {}
        self.auto_counters = {}

    def generate(self, num_rows: int = 5) -> dict:
        """Genera datos de prueba basados en el esquema completo."""
        tables = self.schema.get("tables", {})
        self.generated_data = {}
        self.auto_counters = {}

        sorted_tables = self._sort_tables_by_dependencies(tables)

        for table_name in sorted_tables:
            self.generated_data[table_name] = self._generate_table_data(
                tables[table_name], num_rows
            )

        return self.generated_data

    # --------------------------------------------------------------------------------------------
    def _generate_table_data(self, table_schema: dict, num_rows: int):
        """Genera filas para una tabla específica."""
        rows = []
        table_name = table_schema["name"]
        columns = table_schema["columns"]

        for _ in range(num_rows):
            row = {}
            for col_name, col_def in columns.items():
                # Si es clave foránea → obtener un valor existente
                fk_value = self._get_foreign_key_value(table_name, col_name)
                if fk_value is not None:
                    row[col_name] = fk_value
                else:
                    row[col_name] = self._generate_value(table_name, col_name, col_def)
            rows.append(row)

        return rows

    # --------------------------------------------------------------------------------------------
    def _get_foreign_key_value(self, table_name, column_name):
        """Si la columna es FK, devuelve un valor existente de la tabla referenciada."""
        table = self.schema["tables"][table_name]
        for fk in table.get("foreign_keys", []):
            if column_name in fk["columns"]:
                ref_table = fk["ref_table"]
                ref_col = fk["ref_columns"][0]
                existing_rows = self.generated_data.get(ref_table)
                if existing_rows and len(existing_rows) > 0:
                    return random.choice(existing_rows)[ref_col]
                else:
                    return None
        return None

    # --------------------------------------------------------------------------------------------
    def _generate_value(self, table, column, col_def):
        """Genera un valor según el tipo SQL del campo."""
        col_type = col_def["type"].upper()

        # 🔹 Auto_increment o PK: contador incremental
        if col_def.get("auto_increment") or col_def.get("primary_key"):
            key = (table, column)
            current_value = self.auto_counters.get(key, 0) + 1
            self.auto_counters[key] = current_value
            return current_value

        # 🔹 Tipos comunes
        if col_type.startswith("VARCHAR"):
            col_lower = column.lower()

            if "name" in col_lower:
                return fake.company()
            if "email" in col_lower:
                return fake.unique.email()
            if "phone_number" in col_lower:
                return fake.phone_number()
            if "address" in col_lower:
                return fake.address()
            if "city" in col_lower:
                return fake.city()
            if "state" in col_lower:
                return fake.state()
            if "zip_code" in col_lower:
                return fake.zipcode()
            if "industry" in col_lower:
                return fake.job()
            if "job" in col_lower or "title" in col_lower:
                return fake.job()
            if "location" in col_lower:
                return fake.city()
            if "website" in col_lower:
                return fake.url()
            if "first_name" in col_lower:
                return fake.first_name()
            if "last_name" in col_lower:
                return fake.last_name()
            if "middle_name" in col_lower:
                return fake.middle_name()
            if "role" in col_lower:
                return random.choice(["Developer", "Manager", "Analyst", "Consultant", "Engineer", "Scrum Master"])
            if "benefit" in col_lower:
                return random.choice(["Health Insurance", "Retirement Plan", "Bonus", "Paid Leave"])
            if "status" in col_lower:
                return random.choice(["ACTIVE", "INACTIVE", "PENDING", "APPROVED", "FINAL"])
            return fake.word()

        if col_type.startswith("TEXT"):
            return fake.sentence()
        if col_type.startswith("INT"):
            check = col_def.get("check")
            if check:
                limits = self._parse_check_constraint(check)
                if limits:
                    min_val, max_val = limits
                    return random.randint(min_val, max_val)
            return random.randint(1, 1000)
        if col_type.startswith("DECIMAL"):
            return round(random.uniform(1000, 50000), 2)
        if col_type.startswith("DATE"):
            return str(fake.date_between(start_date="-2y", end_date="today"))
        if col_type.startswith("ENUM"):
            options = col_type[col_type.find("(")+1:col_type.find(")")].replace("'", "").split(",")
            return random.choice([opt.strip() for opt in options])

        return None

    # --------------------------------------------------------------------------------------------
    def _sort_tables_by_dependencies(self, tables: dict) -> list:
        """Ordena las tablas considerando dependencias de claves foráneas."""
        sorted_tables = []
        remaining = dict(tables)

        while remaining:
            progress = False
            for table_name, table_def in list(remaining.items()):
                fks = [fk["ref_table"] for fk in table_def.get("foreign_keys", [])]
                if all(ref in sorted_tables for ref in fks):
                    sorted_tables.append(table_name)
                    del remaining[table_name]
                    progress = True
            if not progress:
                raise ValueError("Ciclo de dependencias detectado en las tablas.")
        return sorted_tables
    
    def _parse_check_constraint(self, check_str):
        """Extrae los límites numéricos de una cláusula CHECK (ej: 'rating >= 1 AND rating <= 5')."""
        if not check_str:
            return None
        
        # Buscar patrones tipo: >= N, <= N
        min_match = re.search(r">=\s*(\d+)", check_str)
        max_match = re.search(r"<=\s*(\d+)", check_str)
        min_val = int(min_match.group(1)) if min_match else None
        max_val = int(max_match.group(1)) if max_match else None
        return (min_val, max_val)
    