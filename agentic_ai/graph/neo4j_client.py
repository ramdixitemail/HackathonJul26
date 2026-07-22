from neo4j import GraphDatabase

class Neo4jClient:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j","test12345")
        )

    def execute(self, query, params=None):

        with self.driver.session() as session:
            return list(session.run(query, params or {}))