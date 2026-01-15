from dataclasses import dataclass, field
from typing import List, Optional
import re

@dataclass
class Column:
    name: str
    raw_type: str
    not_null: bool = False
    default: Optional[str] = None
    is_primary: bool = False
    is_unique: bool = False
    auto_increment: bool = False
    check: Optional[str] = None
    raw: str = ""

@dataclass
class ForeignKey:
    cols: List[str]
    ref_table: str
    ref_cols: List[str]
    raw: str = ""

@dataclass
class Table:
    name: str
    columns: List[Column] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[ForeignKey] = field(default_factory=list)
    raw_body: str = ""

# Helper regexes
CREATE_TABLE_RE = re.compile(r"CREATE\s+TABLE\s+([^\s(]+)\s*\((.*?)\)\s*;", flags=re.IGNORECASE | re.DOTALL)
FK_TABLELEVEL_RE = re.compile(r"FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+([^\s(]+)\s*\(([^)]+)\)", flags=re.IGNORECASE)
PK_TABLELEVEL_RE = re.compile(r"PRIMARY\s+KEY\s*\(([^)]+)\)", flags=re.IGNORECASE)
DEFAULT_RE = re.compile(r"\bDEFAULT\s+(('([^']*)')|(\"([^\"]*)\")|([^\s,]+))", flags=re.IGNORECASE)
NOT_NULL_RE = re.compile(r"\bNOT\s+NULL\b", flags=re.IGNORECASE)
UNIQUE_RE = re.compile(r"\bUNIQUE\b", flags=re.IGNORECASE)
INLINE_PK_RE = re.compile(r"\bPRIMARY\b", flags=re.IGNORECASE)
AUTO_INC_RE = re.compile(r"\bAUTO_INCREMENT\b", flags=re.IGNORECASE)
CHECK_RE = re.compile(r"^\s*CHECK\s*\(", flags=re.IGNORECASE)

def _split_columns_block(body: str) -> List[str]:
    """
    Divide el cuerpo del CREATE TABLE en ítems separados por comas,
    pero evita cortar dentro de paréntesis o dentro de comillas simples/dobles.
    Maneja correctamente ENUM('A','B'), CHECK(...) y DEFAULT 'x,y'.
    """
    items = []
    current = []
    depth = 0
    in_single_quote = False
    in_double_quote = False

    for ch in body:
        if ch == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            current.append(ch)
        elif ch == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current.append(ch)
        elif ch == "(" and not in_single_quote and not in_double_quote:
            depth += 1
            current.append(ch)
        elif ch == ")" and not in_single_quote and not in_double_quote:
            depth = max(0, depth - 1)
            current.append(ch)
        elif ch == "," and depth == 0 and not in_single_quote and not in_double_quote:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
        else:
            current.append(ch)

    last = "".join(current).strip()
    if last:
        items.append(last)

    # Filtrar líneas vacías o comentarios completos
    return [it.strip().rstrip(",") for it in items if it.strip() and not it.strip().startswith("--")]

def _extract_type(rest: str) -> (str, str):
    """
    Dado el resto de la definición (después del nombre), extrae el tipo completo
    (ej 'VARCHAR(255)', 'ENUM('a','b')', 'DECIMAL(10,2)', 'INT', 'TEXT') y devuelve
    (tipo, restante_constraints).
    Maneja paréntesis y comillas dentro del paréntesis.
    """
    rest = rest.strip()
    if not rest:
        return "", ""
    # Si comienza con un identificador seguido de paréntesis, extraer hasta paréntesis emparejado
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\()", rest)
    if m:
        typename = m.group(1)
        # encontrar el cierre correspondiente desde m.start(2)
        start_idx = m.start(2)  # position of '('
        i = start_idx
        depth = 0
        in_single = False
        in_double = False
        while i < len(rest):
            ch = rest[i]
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "(" and not in_single and not in_double:
                depth += 1
            elif ch == ")" and not in_single and not in_double:
                depth -= 1
                if depth == 0:
                    # include closing paren
                    type_str = rest[:i+1].strip()
                    remaining = rest[i+1:].strip()
                    return type_str, remaining
            i += 1
        # si no empareja, fallback: toma hasta primer espacio
        parts = rest.split(None, 1)
        if len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], parts[1]
    else:
        # tipo sin paréntesis: toma la primera palabra como tipo
        parts = rest.split(None, 1)
        if len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], parts[1]

def parse_column_definition(item_core: str):
    """
    Parsea una línea de definición de columna y devuelve un dict con:
    name, col_type, not_null, default, is_unique, is_primary, auto_increment, raw
    Si la línea no parece ser una definición de columna, devuelve None.
    """
    item_core = item_core.strip().rstrip(",")
    # debe empezar con un nombre válido
    m = re.match(r'^\s*("?[\w\d_]+"?)\s+(.*)$', item_core)
    if not m:
        return None
    col_name = m.group(1).strip().strip('"')
    rest = m.group(2).strip()
    if rest == "":
        return None
    # extraer tipo completo
    col_type, constraints = _extract_type(rest)
    # ahora constraints contiene "NOT NULL DEFAULT 'x' UNIQUE ..." or similar
    
    # Detectar CHECK(...)
    check_val = None
    check_match = re.search(r"CHECK\s*\((.*?)\)", constraints, flags=re.IGNORECASE)
    if check_match:
        check_val = check_match.group(1).strip()

    not_null = bool(NOT_NULL_RE.search(constraints))
    unique = bool(UNIQUE_RE.search(constraints))
    default_val = None
    def_m = DEFAULT_RE.search(constraints)
    if def_m:
        default_val = def_m.group(1).strip()
    inline_pk = bool(INLINE_PK_RE.search(constraints)) or bool(re.search(r"\bPRIMARY\s+KEY\b", constraints, flags=re.IGNORECASE))
    auto_inc = bool(AUTO_INC_RE.search(constraints))
    return {
        "name": col_name,
        "raw_type": col_type,
        "not_null": not_null,
        "default": default_val,
        "is_primary": inline_pk,
        "is_unique": unique,
        "auto_increment": auto_inc,
        "check": check_val,
        "raw": item_core,
    }

def parse_ddl_text(ddl_text: str) -> List[Table]:
    tables: List[Table] = []
    text = ddl_text.replace("\r\n", "\n")

    for match in CREATE_TABLE_RE.finditer(text):
        tbl_name = match.group(1).strip().strip('"')
        body = match.group(2).strip()
        table = Table(name=tbl_name, raw_body=body)

        items = _split_columns_block(body)
        for item in items:
            inline_comment = None
            if "--" in item:
                parts = item.split("--", 1)
                item_core = parts[0].strip()
                inline_comment = parts[1].strip()
            else:
                item_core = item.strip()

            # ignore empty
            if not item_core:
                continue

            # table-level FK
            fk_match = FK_TABLELEVEL_RE.search(item_core)
            if fk_match:
                cols = [c.strip().strip('"') for c in fk_match.group(1).split(",")]
                ref_table = fk_match.group(2).strip().strip('"')
                ref_cols = [c.strip().strip('"') for c in fk_match.group(3).split(",")]
                table.foreign_keys.append(ForeignKey(cols=cols, ref_table=ref_table, ref_cols=ref_cols, raw=item_core))
                continue

            # table-level PK
            pk_match = PK_TABLELEVEL_RE.search(item_core)
            if pk_match:
                pk_cols = [c.strip().strip('"') for c in pk_match.group(1).split(",")]
                for pk in pk_cols:
                    if pk not in table.primary_keys:
                        table.primary_keys.append(pk)
                continue

            # ignore pure constraints lines (CHECK, CONSTRAINT, UNIQUE at table level)
            if item_core.strip().upper().startswith(("CONSTRAINT", "CHECK", "UNIQUE", "KEY", "INDEX")):
                continue

            # try parse as column definition
            parsed = parse_column_definition(item_core)
            if parsed:
                col = Column(
                    name=parsed["name"],
                    raw_type=parsed["raw_type"],
                    not_null=parsed["not_null"],
                    default=parsed["default"],
                    is_primary=parsed["is_primary"],
                    is_unique=parsed["is_unique"],
                    auto_increment=parsed["auto_increment"],
                    check=parsed.get("check"),
                    raw=parsed["raw"],
                )
                table.columns.append(col)
                if parsed["is_primary"] and col.name not in table.primary_keys:
                    table.primary_keys.append(col.name)
                # heurística: si hay inline comment que mencione FK/reference
                if inline_comment:
                    if "foreign key" in inline_comment.lower() or "references" in inline_comment.lower():
                        ref_search = re.search(r"to\s+([A-Za-z0-9_]+)\s+table", inline_comment, flags=re.IGNORECASE)
                        if ref_search:
                            ref_tbl = ref_search.group(1)
                            table.foreign_keys.append(
                                ForeignKey(
                                    cols=[col.name],
                                    ref_table=ref_tbl,
                                    ref_cols=[f"{col.name.split('_')[0]}_id"],
                                    raw=f"comment:{inline_comment}",
                                )
                            )
                continue

            # fallback: if none matched, keep raw as-is for manual inspection (rare)
            table.columns.append(Column(name=f"_raw_{len(table.columns)+1}", raw_type="", raw=item_core))
        tables.append(table)
    return tables

def parse_ddl_file(path: str) -> List[Table]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_ddl_text(text)

def tables_dependency_order(tables: List[Table]) -> List[str]:
    adj = {t.name: set() for t in tables}
    indeg = {t.name: 0 for t in tables}
    for t in tables:
        for fk in t.foreign_keys:
            ref = fk.ref_table
            if ref == t.name:
                continue
            if ref in adj:
                if t.name not in adj[ref]:
                    adj[ref].add(t.name)
                    indeg[t.name] += 1
    q = [name for name, d in indeg.items() if d == 0]
    order = []
    while q:
        n = q.pop(0)
        order.append(n)
        for neigh in list(adj[n]):
            indeg[neigh] -= 1
            adj[n].remove(neigh)
            if indeg[neigh] == 0:
                q.append(neigh)
    remaining = [t.name for t in tables if t.name not in order]
    order.extend(remaining)
    return order

def print_tables_summary(tables: List[Table]):
    for t in tables:
        print(f"TABLE: {t.name}")
        print("  Columns:")
        for c in t.columns:
            pk = " PK" if c.is_primary else ""
            ai = " AUTO_INCREMENT" if c.auto_increment else ""
            nn = " NOT NULL" if c.not_null else ""
            uniq = " UNIQUE" if c.is_unique else ""
            default = f" DEFAULT {c.default}" if c.default else ""
            check = f" CHECK ({c.check})" if c.check else ""
            print(f"    - {c.name} : {c.raw_type}{ai}{pk}{nn}{uniq}{default}{check}")
        if t.primary_keys:
            print(f"  Primary keys: {t.primary_keys}")
        if t.foreign_keys:
            for fk in t.foreign_keys:
                print(f"  FK: {fk.cols} -> {fk.ref_table}({fk.ref_cols})")
        print()
