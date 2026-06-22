"""
Builds a directed graph of foreign key relationships across all schemas.

The graph lets us find the JOIN path between any two tables automatically.
Nodes are table names. Edges are FKs, with the join clause stored as metadata.
"""

from __future__ import annotations

import networkx as nx


class FKGraph:
    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()

    def build_from_metadata(self, schema_metadata: dict) -> None:
        """Populate the graph from the SCHEMA_METADATA dict."""
        for db_name, db_info in schema_metadata.items():
            for table_name in db_info.get("tables", {}):
                self.graph.add_node(table_name, database=db_name)

            for fk in db_info.get("foreign_keys", []):
                from_table = fk["from_table"]
                from_col = fk["from_column"]
                to_table = fk["to_table"]
                to_col = fk["to_column"]

                join_clause = (
                    f"JOIN {to_table} ON {from_table}.{from_col} = {to_table}.{to_col}"
                )
                self.graph.add_edge(
                    from_table,
                    to_table,
                    from_column=from_col,
                    to_column=to_col,
                    join_clause=join_clause,
                )
                # Add the reverse edge so shortest-path works in both directions.
                reverse_clause = (
                    f"JOIN {from_table} ON {to_table}.{to_col} = {from_table}.{from_col}"
                )
                if not self.graph.has_edge(to_table, from_table):
                    self.graph.add_edge(
                        to_table,
                        from_table,
                        from_column=to_col,
                        to_column=from_col,
                        join_clause=reverse_clause,
                    )

    def get_join_path(self, source: str, target: str) -> list[str]:
        """
        Return ordered JOIN clauses connecting source to target.
        Returns an empty list if source == target or no path exists.
        """
        if source == target:
            return []
        try:
            node_path = nx.shortest_path(self.graph, source=source, target=target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

        joins: list[str] = []
        for i in range(len(node_path) - 1):
            edge_data = self.graph[node_path[i]][node_path[i + 1]]
            joins.append(edge_data["join_clause"])
        return joins

    def get_join_clauses_for_tables(self, tables: list[str]) -> list[str]:
        """
        Given a list of relevant tables, return the minimal set of JOIN clauses
        that connects all of them using a greedy spanning approach.

        We anchor to the first table and find paths from it to every other table,
        collecting unique JOIN clauses along the way.
        """
        if len(tables) <= 1:
            return []

        seen_clauses: set[str] = set()
        result: list[str] = []
        anchor = tables[0]

        for target in tables[1:]:
            for clause in self.get_join_path(anchor, target):
                if clause not in seen_clauses:
                    seen_clauses.add(clause)
                    result.append(clause)

        return result

    def tables_in_graph(self) -> list[str]:
        return list(self.graph.nodes)
