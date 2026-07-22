"""
schema_agent.py

Discovers the Neo4j schema dynamically and provides
a schema description for Cypher generation.
"""

from graph.neo4j_client import Neo4jClient


class SchemaAgent:

    def __init__(self):

        self.neo4j = Neo4jClient()

        self.schema_cache = None

    # ---------------------------------------------------------

    def get_labels(self):

        query = """
        CALL db.labels()
        """

        rows = self.neo4j.execute(query)

        labels = []

        for row in rows:
            labels.append(row["label"])

        print("==============lebels==============",labels)
        return sorted(labels)

    # ---------------------------------------------------------

    def get_relationship_types(self):

        query = """
        CALL db.relationshipTypes()
        """

        rows = self.neo4j.execute(query)

        relationships = []

        for row in rows:
            relationships.append(row["relationshipType"])

        return sorted(relationships)

    # ---------------------------------------------------------

    def get_property_keys(self):

        query = """
        CALL db.propertyKeys()
        """

        rows = self.neo4j.execute(query)

        keys = []

        for row in rows:
            keys.append(row["propertyKey"])

        return sorted(keys)

    # ---------------------------------------------------------

    def get_node_properties(self):

        labels = self.get_labels()

        result = {}

        for label in labels:

            query = f"""
            MATCH (n:{label})
            RETURN keys(n) AS keys
            LIMIT 1
            """

            rows = self.neo4j.execute(query)

            if rows:

                result[label] = rows[0]["keys"]

            else:

                result[label] = []

        return result

    # ---------------------------------------------------------

    def get_relationship_properties(self):

        relationship_types = self.get_relationship_types()

        result = {}

        for rel in relationship_types:

            query = f"""
            MATCH ()-[r:{rel}]->()
            RETURN keys(r) AS keys
            LIMIT 1
            """

            rows = self.neo4j.execute(query)

            if rows:

                result[rel] = rows[0]["keys"]

            else:

                result[rel] = []

        return result

    # ---------------------------------------------------------

    def build_schema_prompt(self):

        labels = self.get_labels()

        relationships = self.get_relationship_types()

        node_properties = self.get_node_properties()

        relationship_properties = self.get_relationship_properties()

        prompt = []

        prompt.append("Neo4j Knowledge Graph Schema\n")

        prompt.append("NODE LABELS\n")

        for label in labels:

            props = ", ".join(node_properties[label])

            prompt.append(
                f"- {label} ({props})"
            )

        prompt.append("\nRELATIONSHIP TYPES\n")

        for rel in relationships:

            props = ", ".join(
                relationship_properties[rel]
            )

            prompt.append(
                f"- {rel} ({props})"
            )

        return "\n".join(prompt)

    # ---------------------------------------------------------

    def get_schema(self):

        if self.schema_cache is None:

            self.schema_cache = self.build_schema_prompt()

        return self.schema_cache

    # ---------------------------------------------------------

    def refresh(self):

        self.schema_cache = None

        return self.get_schema()