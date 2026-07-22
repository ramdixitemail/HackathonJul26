"""
query_agent.py

Executes Cypher queries against Neo4j.
"""

from graph.neo4j_client import Neo4jClient


class QueryAgent:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def execute(self, cypher):

        print("\n" + "=" * 80)
        print("EXECUTING CYPHER")
        print("=" * 80)
        print(cypher)
        print("=" * 80)

        try:

            rows = self.neo4j.execute(cypher)

            result = []

            for row in rows:

                d = {}

                for key in row.keys():

                    value = row[key]

                    try:
                        d[key] = dict(value)
                    except Exception:
                        d[key] = value

                result.append(d)

            print("\nRows Returned :", len(result))

            return {
                "cypher": cypher,
                "row_count": len(rows),
                "rows": rows
            }

        except Exception as ex:

            print("Neo4j Error :", ex)

            raise