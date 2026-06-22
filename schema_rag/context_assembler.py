"""
Dynamic prompt context assembler.

Combines schema RAG results, FK join paths, and disambiguation notes into
a single formatted context block that gets injected into every LLM prompt.
"""

from __future__ import annotations

from typing import Any

from datasets.schema_metadata import SCHEMA_METADATA
from schema_rag.disambiguation import ColumnDisambiguator
from schema_rag.fk_graph import FKGraph
from schema_rag.vector_store import VectorStore


def _default_fk_graph() -> FKGraph:
    g = FKGraph()
    g.build_from_metadata(SCHEMA_METADATA)
    return g


class ContextAssembler:
    def __init__(
        self,
        vector_store: VectorStore | None = None,
        fk_graph: FKGraph | None = None,
        disambiguator: ColumnDisambiguator | None = None,
        top_k: int = 15,
        schema_version: str = "v1",
    ) -> None:
        self.vector_store = vector_store or VectorStore()
        self.fk_graph = fk_graph or _default_fk_graph()
        self.disambiguator = disambiguator or ColumnDisambiguator(SCHEMA_METADATA)
        self.top_k = top_k
        self.schema_version = schema_version

    def assemble(self, query: str, schema_version: str | None = None) -> str:
        """
        Build and return the schema context string for injection into LLM prompts.
        """
        version = schema_version or self.schema_version
        raw_results = self.vector_store.search(
            query=query,
            top_k=self.top_k,
            schema_version=version,
        )

        relevant_tables = self._extract_tables(raw_results)
        join_clauses = self.fk_graph.get_join_clauses_for_tables(relevant_tables)
        disambiguation_notes = self.disambiguator.get_disambiguation_notes(raw_results)

        return self._format_context(
            question=query,
            raw_results=raw_results,
            relevant_tables=relevant_tables,
            join_clauses=join_clauses,
            disambiguation_notes=disambiguation_notes,
        )

    def _extract_tables(self, results: list[dict[str, Any]]) -> list[str]:
        seen: set[str] = set()
        tables: list[str] = []
        for row in results:
            t = row.get("table_name")
            if t and t not in seen:
                seen.add(t)
                tables.append(t)
        return tables

    def _format_context(
        self,
        question: str,
        raw_results: list[dict[str, Any]],
        relevant_tables: list[str],
        join_clauses: list[str],
        disambiguation_notes: list[str],
    ) -> str:
        lines: list[str] = []

        lines.append("=== RELEVANT SCHEMA CONTEXT ===")
        lines.append(f"User question: {question}")
        lines.append("")
        lines.append("IMPORTANT: Tables belong to separate databases. NEVER join across databases.")
        lines.append("")

        # Group tables by database prefix so the LLM cannot mistake cross-DB joins
        db_to_tables: dict[str, list[str]] = {}
        for table in relevant_tables:
            prefix = table.split("_")[0] if "_" in table else "other"
            db_to_tables.setdefault(prefix, []).append(table)

        db_names = {"nw": "Northwind", "tpch": "TPC-H", "nyc": "NYC Taxi", "ut": "User Upload"}
        lines.append("Relevant tables (grouped by database):")
        for prefix, tables in db_to_tables.items():
            db_label = db_names.get(prefix, prefix)
            lines.append(f"  [{db_label} database - prefix '{prefix}_']")
            for t in tables:
                lines.append(f"    - {t}")
        lines.append("")

        lines.append("Relevant columns:")
        for row in raw_results:
            if row.get("entry_type") == "column":
                col = row.get("column_name", "")
                table = row.get("table_name", "")
                dtype = row.get("data_type", "")
                desc = row.get("description", "")
                samples = row.get("sample_values")
                sample_str = ""
                if samples:
                    import json
                    vals = json.loads(samples) if isinstance(samples, str) else samples
                    sample_str = f" [e.g. {', '.join(str(v) for v in vals[:3])}]"
                lines.append(f"  - {table}.{col} ({dtype}): {desc}{sample_str}")
        lines.append("")

        if join_clauses:
            lines.append("Required JOINs to connect these tables:")
            for clause in join_clauses:
                lines.append(f"  {clause}")
            lines.append("")

        if disambiguation_notes:
            lines.append("Column disambiguation:")
            for note in disambiguation_notes:
                lines.append(note)
            lines.append("")

        fk_entries = [r for r in raw_results if r.get("entry_type") == "foreign_key"]
        if fk_entries:
            lines.append("Foreign key relationships:")
            for row in fk_entries:
                lines.append(f"  - {row.get('fk_references', '')}")
            lines.append("")

        lines.append("=== END SCHEMA CONTEXT ===")

        return "\n".join(lines)
