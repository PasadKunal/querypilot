"""
Structural tests for SCHEMA_METADATA.

These verify that the metadata dictionary is internally consistent:
every FK references tables and columns that actually exist, every table
has at least one column, and required fields are present. If any of
these fail it means the metadata was edited incorrectly and the embedder
or FK graph will break at runtime.
"""

from __future__ import annotations

from datasets.schema_metadata import SCHEMA_METADATA

EXPECTED_DATABASES = {"northwind", "tpch", "nyc_taxi"}
EXPECTED_TABLE_COUNTS = {"northwind": 8, "tpch": 8, "nyc_taxi": 4}


class TestSchemaMetadataStructure:
    def test_expected_databases_present(self):
        assert set(SCHEMA_METADATA.keys()) == EXPECTED_DATABASES

    def test_each_database_has_description(self):
        for db, info in SCHEMA_METADATA.items():
            assert "description" in info, f"{db} missing 'description'"
            assert info["description"], f"{db} description is empty"

    def test_each_database_has_tables(self):
        for db, info in SCHEMA_METADATA.items():
            assert "tables" in info, f"{db} missing 'tables'"
            assert len(info["tables"]) > 0, f"{db} has no tables"

    def test_table_counts_match_expected(self):
        for db, expected in EXPECTED_TABLE_COUNTS.items():
            actual = len(SCHEMA_METADATA[db]["tables"])
            assert actual == expected, (
                f"{db} expected {expected} tables, got {actual}"
            )

    def test_each_table_has_description_and_columns(self):
        for db, info in SCHEMA_METADATA.items():
            for table, meta in info["tables"].items():
                assert "description" in meta, f"{db}.{table} missing 'description'"
                assert "columns" in meta, f"{db}.{table} missing 'columns'"
                assert len(meta["columns"]) > 0, f"{db}.{table} has no columns"

    def test_each_column_has_type_and_description(self):
        for db, info in SCHEMA_METADATA.items():
            for table, meta in info["tables"].items():
                for col, col_meta in meta["columns"].items():
                    assert "type" in col_meta, f"{db}.{table}.{col} missing 'type'"
                    assert "description" in col_meta, f"{db}.{table}.{col} missing 'description'"

    def test_foreign_keys_reference_existing_tables_and_columns(self):
        all_tables: dict[str, set[str]] = {}
        for db, info in SCHEMA_METADATA.items():
            for table, meta in info["tables"].items():
                all_tables[table] = set(meta["columns"].keys())

        for db, info in SCHEMA_METADATA.items():
            for fk in info.get("foreign_keys", []):
                from_table = fk["from_table"]
                from_col = fk["from_column"]
                to_table = fk["to_table"]
                to_col = fk["to_column"]

                assert from_table in all_tables, (
                    f"FK references unknown from_table '{from_table}'"
                )
                assert from_col in all_tables[from_table], (
                    f"FK references unknown column '{from_table}.{from_col}'"
                )
                assert to_table in all_tables, (
                    f"FK references unknown to_table '{to_table}'"
                )
                assert to_col in all_tables[to_table], (
                    f"FK references unknown column '{to_table}.{to_col}'"
                )

    def test_no_cross_database_foreign_keys(self):
        """FKs should only connect tables within the same database."""
        for db, info in SCHEMA_METADATA.items():
            own_tables = set(info["tables"].keys())
            for fk in info.get("foreign_keys", []):
                assert fk["from_table"] in own_tables, (
                    f"{db} FK from_table '{fk['from_table']}' not in {db}"
                )
                assert fk["to_table"] in own_tables, (
                    f"{db} FK to_table '{fk['to_table']}' not in {db}"
                )

    def test_sample_values_are_lists_when_present(self):
        for db, info in SCHEMA_METADATA.items():
            for table, meta in info["tables"].items():
                for col, col_meta in meta["columns"].items():
                    sv = col_meta.get("sample_values")
                    if sv is not None:
                        assert isinstance(sv, list), (
                            f"{db}.{table}.{col} sample_values must be a list"
                        )
