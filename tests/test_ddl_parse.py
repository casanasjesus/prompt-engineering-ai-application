import os
import sys

# 1) Determinar el directorio raíz del proyecto (dos niveles arriba si este archivo está en tests/)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
# 2) Añadir la carpeta 'src' al inicio de sys.path para poder importar módulos dentro de src
sys.path.insert(0, os.path.join(base_dir, "src"))

# Ahora podemos importar ddl_parser directamente (sin prefijo src.)
from ddl_parser import parse_ddl_file, print_tables_summary, tables_dependency_order

# Ruta segura al archivo DDL
ddl_path = os.path.join(base_dir, "src", "ddl", "company_employee_schema.ddl")

tables = parse_ddl_file(ddl_path)

print_tables_summary(tables)
print("Orden sugerido para generación:")
print(tables_dependency_order(tables))
