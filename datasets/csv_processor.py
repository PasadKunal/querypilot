"""
CSV ingestion helper: parse bytes into typed rows and PostgreSQL column type map.
"""
from __future__ import annotations

import io
import re
from typing import Any

import pandas as pd

_PG_TYPE: dict[str, str] = {
    "int64": "BIGINT",
    "Int64": "BIGINT",
    "float64": "NUMERIC",
    "Float64": "NUMERIC",
    "bool": "BOOLEAN",
    "boolean": "BOOLEAN",
    "object": "TEXT",
    "string": "TEXT",
    "datetime64[ns]": "TIMESTAMP",
    "datetime64[us]": "TIMESTAMP",
}


def clean_column_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        return "col"
    if name[0].isdigit():
        name = "col_" + name
    return name[:63]


def parse_csv(content: bytes, filename: str = "data.csv") -> tuple[list[str], list[dict[str, Any]], dict[str, str]]:
    """
    Parse CSV or Excel bytes.
    Returns (cleaned_headers, row_dicts, {col_name: pg_type}).
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "csv"
    if ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(content), dtype_backend="numpy_nullable")
    else:
        text = content.decode("utf-8-sig", errors="replace")
        df = pd.read_csv(io.StringIO(text), dtype_backend="numpy_nullable")

    if df is None or df.empty or df.shape[0] == 0:
        raise ValueError("CSV file has no data rows")

    seen: dict[str, int] = {}
    new_cols: list[str] = []
    for col in df.columns:
        clean = clean_column_name(str(col))
        if clean in seen:
            seen[clean] += 1
            clean = f"{clean}_{seen[clean]}"
        else:
            seen[clean] = 0
        new_cols.append(clean)
    df.columns = new_cols

    col_types: dict[str, str] = {}
    for col in df.columns:
        col_types[col] = _PG_TYPE.get(str(df[col].dtype), "TEXT")

    rows = df.where(pd.notnull(df), None).to_dict(orient="records")
    return list(df.columns), rows, col_types
