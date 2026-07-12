"""Validate committed methods data against the repo schemas. Run in CI on every PR.

For each ``data/<NN>-<datasource>/`` folder:
  - ``metadata.json`` is validated against ``schema/metadata.schema.json`` (JSON Schema).
  - each parquet named by a column-schema (``method.yaml`` / ``characterization-factor.yaml``
    / ``normalization-weighting.yaml``) is checked for: all ``required`` columns present,
    column dtypes compatible with the schema, ``primary_key`` uniqueness, and
    ``foreign_key`` referential integrity (e.g. every CF ``method_id`` exists in methods).

Empty scaffold folders (metadata only, no parquet yet) validate as long as their metadata
is well-formed. Exits non-zero if any datasource has errors.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import pyarrow.parquet as pq
import pyarrow.types as pat
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
DATA_DIR = ROOT / "data"
METADATA_SCHEMA = json.loads((SCHEMA_DIR / "metadata.schema.json").read_text())
TABLE_SCHEMA_FILES = ("method.yaml", "characterization-factor.yaml", "normalization-weighting.yaml")


def _type_ok(schema_type: str, pa_type) -> bool:
    """Whether a parquet column type satisfies the plain-YAML schema type (lenient)."""
    if schema_type == "string":
        return pat.is_string(pa_type) or pat.is_large_string(pa_type)
    if schema_type == "double":
        return pat.is_floating(pa_type)
    if schema_type == "int":
        return pat.is_integer(pa_type)
    if schema_type == "date":  # dates may be stored as native date or ISO string
        return (
            pat.is_date(pa_type)
            or pat.is_timestamp(pa_type)
            or pat.is_string(pa_type)
            or pat.is_large_string(pa_type)
        )
    return True  # unknown schema type -> don't block


def _load_table_schemas() -> dict[str, dict]:
    """Map parquet filename -> its column-schema dict."""
    schemas: dict[str, dict] = {}
    for name in TABLE_SCHEMA_FILES:
        schema = yaml.safe_load((SCHEMA_DIR / name).read_text())
        schemas[schema["file"]] = schema
    return schemas


def validate_datasource(ds: Path, table_schemas: dict[str, dict], errors: list[str]) -> None:
    meta_path = ds / "metadata.json"
    if not meta_path.exists():
        errors.append(f"{ds.name}: missing metadata.json")
        return
    try:
        jsonschema.validate(json.loads(meta_path.read_text()), METADATA_SCHEMA)
    except jsonschema.ValidationError as exc:
        errors.append(f"{ds.name}/metadata.json: {exc.message}")

    present: dict[str, Path] = {}
    pk_values: dict[str, set] = {}  # table name -> primary-key value set (for FK checks)

    for fname, schema in table_schemas.items():
        path = ds / fname
        if not path.exists():
            continue
        present[fname] = path
        columns = {field.name: field.type for field in pq.read_schema(path)}
        for col in schema["columns"]:
            name = col["name"]
            if col.get("required") and name not in columns:
                errors.append(f"{ds.name}/{fname}: missing required column '{name}'")
            elif name in columns and not _type_ok(col["type"], columns[name]):
                errors.append(
                    f"{ds.name}/{fname}: column '{name}' expected {col['type']}, got {columns[name]}"
                )
        pk = schema.get("primary_key")
        if pk and pk in columns:
            values = pq.read_table(path, columns=[pk]).column(pk).to_pylist()
            if len(values) != len(set(values)):
                errors.append(f"{ds.name}/{fname}: primary_key '{pk}' has duplicate values")
            pk_values[schema["table"]] = set(values)

    for fname, path in present.items():
        for col, ref in (table_schemas[fname].get("foreign_key") or {}).items():
            ref_table, _ref_col = ref.split(".")
            if ref_table not in pk_values:
                continue  # referenced table absent in this datasource — nothing to check
            values = set(pq.read_table(path, columns=[col]).column(col).to_pylist())
            missing = values - pk_values[ref_table]
            if missing:
                sample = sorted(str(m) for m in missing)[:3]
                errors.append(
                    f"{ds.name}/{fname}: {len(missing)} '{col}' value(s) not in {ref} "
                    f"(e.g. {sample})"
                )


def main() -> int:
    table_schemas = _load_table_schemas()
    errors: list[str] = []
    datasources = sorted(p for p in DATA_DIR.iterdir() if p.is_dir())
    for ds in datasources:
        validate_datasource(ds, table_schemas, errors)
    if errors:
        print("Data validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"Data validation passed: {len(datasources)} datasource(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
