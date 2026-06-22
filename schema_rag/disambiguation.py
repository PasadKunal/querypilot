"""
Column disambiguation using sample value injection.

When multiple retrieved columns share similar names across different tables
(e.g., nw_orders.ship_country vs nw_customers.country), we surface sample
values for each so the LLM can distinguish them without guessing.
"""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any


class ColumnDisambiguator:
    def __init__(self, schema_metadata: dict) -> None:
        self.schema_metadata = schema_metadata
        self._column_index = self._build_column_index()

    def _build_column_index(self) -> dict[str, list[dict[str, Any]]]:
        """Maps bare column names to all (table, metadata) pairs that have that name."""
        index: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for db_name, db_info in self.schema_metadata.items():
            for table_name, table_info in db_info.get("tables", {}).items():
                for col_name, col_info in table_info.get("columns", {}).items():
                    index[col_name].append({
                        "database": db_name,
                        "table": table_name,
                        "column": col_name,
                        "type": col_info.get("type", ""),
                        "description": col_info.get("description", ""),
                        "sample_values": col_info.get("sample_values", []),
                    })
        return dict(index)

    def get_disambiguation_notes(self, retrieved_entries: list[dict[str, Any]]) -> list[str]:
        """
        Look at the retrieved schema entries. For any column name that appears in
        more than one of the retrieved tables, return a disambiguation note with
        sample values for each occurrence so the LLM can tell them apart.
        """
        retrieved_columns: dict[str, list[str]] = defaultdict(list)
        for entry in retrieved_entries:
            if entry.get("entry_type") == "column" and entry.get("column_name"):
                retrieved_columns[entry["column_name"]].append(entry["table_name"])

        notes: list[str] = []
        for col_name, tables in retrieved_columns.items():
            unique_tables = list(dict.fromkeys(tables))
            if len(unique_tables) < 2:
                continue

            note_parts = [f"NOTE: '{col_name}' appears in multiple tables:"]
            for table in unique_tables:
                col_meta = self._get_column_meta(table, col_name)
                if col_meta:
                    samples = ", ".join(str(v) for v in col_meta["sample_values"][:3])
                    note_parts.append(
                        f"  - {table}.{col_name} ({col_meta['type']}): {col_meta['description']}. "
                        f"Sample values: {samples}"
                    )
            notes.append("\n".join(note_parts))

        return notes

    def _get_column_meta(self, table_name: str, col_name: str) -> dict[str, Any] | None:
        for entry in self._column_index.get(col_name, []):
            if entry["table"] == table_name:
                return entry
        return None
