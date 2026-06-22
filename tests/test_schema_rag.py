"""
Unit tests for schema RAG components.

FKGraph and ColumnDisambiguator are tested against real SCHEMA_METADATA
without any database connection. VectorStore and ContextAssembler tests
require a live Supabase connection and are skipped in CI.
"""

import pytest

from datasets.schema_metadata import SCHEMA_METADATA
from schema_rag.disambiguation import ColumnDisambiguator
from schema_rag.fk_graph import FKGraph


@pytest.fixture(scope="module")
def fk_graph() -> FKGraph:
    g = FKGraph()
    g.build_from_metadata(SCHEMA_METADATA)
    return g


@pytest.fixture(scope="module")
def disambiguator() -> ColumnDisambiguator:
    return ColumnDisambiguator(SCHEMA_METADATA)


class TestFKGraph:
    def test_all_tables_loaded(self, fk_graph: FKGraph):
        tables = fk_graph.tables_in_graph()
        assert "nw_orders" in tables
        assert "nw_customers" in tables
        assert "tpch_lineitem" in tables
        assert "nyc_trips" in tables

    def test_direct_join_path(self, fk_graph: FKGraph):
        path = fk_graph.get_join_path("nw_orders", "nw_customers")
        assert len(path) == 1
        assert "nw_customers" in path[0]
        assert "customer_id" in path[0]

    def test_two_hop_join_path(self, fk_graph: FKGraph):
        # nw_order_details -> nw_orders -> nw_customers
        path = fk_graph.get_join_path("nw_order_details", "nw_customers")
        assert len(path) == 2

    def test_same_table_returns_empty(self, fk_graph: FKGraph):
        path = fk_graph.get_join_path("nw_orders", "nw_orders")
        assert path == []

    def test_no_path_across_schemas(self, fk_graph: FKGraph):
        # Northwind and TPC-H are not linked by FKs
        path = fk_graph.get_join_path("nw_orders", "tpch_lineitem")
        assert path == []

    def test_join_clauses_for_multiple_tables(self, fk_graph: FKGraph):
        tables = ["nw_orders", "nw_customers", "nw_order_details"]
        clauses = fk_graph.get_join_clauses_for_tables(tables)
        assert len(clauses) >= 2
        full_text = " ".join(clauses)
        assert "nw_customers" in full_text
        assert "nw_order_details" in full_text

    def test_single_table_returns_no_joins(self, fk_graph: FKGraph):
        clauses = fk_graph.get_join_clauses_for_tables(["nw_orders"])
        assert clauses == []

    def test_nyc_trips_to_zones_join(self, fk_graph: FKGraph):
        path = fk_graph.get_join_path("nyc_trips", "nyc_taxi_zones")
        assert len(path) == 1
        assert "nyc_taxi_zones" in path[0]


class TestColumnDisambiguator:
    def test_no_ambiguity_single_entry(self, disambiguator: ColumnDisambiguator):
        entries = [
            {"entry_type": "column", "table_name": "nw_orders", "column_name": "freight"},
        ]
        notes = disambiguator.get_disambiguation_notes(entries)
        assert notes == []

    def test_detects_ambiguous_columns(self, disambiguator: ColumnDisambiguator):
        # country appears in nw_customers, nw_employees, and nw_suppliers
        entries = [
            {"entry_type": "column", "table_name": "nw_customers", "column_name": "country"},
            {"entry_type": "column", "table_name": "nw_employees", "column_name": "country"},
        ]
        notes = disambiguator.get_disambiguation_notes(entries)
        assert len(notes) == 1
        assert "country" in notes[0]
        assert "nw_customers" in notes[0]
        assert "nw_employees" in notes[0]

    def test_ignores_non_column_entries(self, disambiguator: ColumnDisambiguator):
        entries = [
            {"entry_type": "table", "table_name": "nw_orders", "column_name": None},
            {"entry_type": "foreign_key", "table_name": "nw_orders", "column_name": "customer_id"},
        ]
        notes = disambiguator.get_disambiguation_notes(entries)
        assert notes == []

    def test_sample_values_in_note(self, disambiguator: ColumnDisambiguator):
        entries = [
            {"entry_type": "column", "table_name": "nw_customers", "column_name": "country"},
            {"entry_type": "column", "table_name": "nw_suppliers", "column_name": "country"},
        ]
        notes = disambiguator.get_disambiguation_notes(entries)
        assert len(notes) == 1
        assert "Germany" in notes[0] or "UK" in notes[0]
