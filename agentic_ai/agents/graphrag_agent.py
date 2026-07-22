from agents.schema_agent import SchemaAgent
from agents.cypher_agent import CypherAgent
from agents.retrieval_agent import RetrievalAgent
from agents.query_agent import QueryAgent

from llm.ollama_client import OllamaClient


class GraphRAGAgent:

    def __init__(self):

        self.schema_agent = SchemaAgent()
        self.cypher_agent = CypherAgent()
        self.query_agent = QueryAgent()
        self.retrieval_agent = RetrievalAgent()
        self.llm = OllamaClient()

    def ask(self, question):

        try:

            print("=" * 80)
            print("QUESTION")
            print("=" * 80)
            print(question)

            # ---------------------------------------------------------
            # Get Graph Schema
            # ---------------------------------------------------------

            schema = self.schema_agent.get_schema()

            print("=" * 80)
            print("SCHEMA")
            print("=" * 80)
            print(schema)

            # ---------------------------------------------------------
            # Generate Cypher
            # ---------------------------------------------------------

            cypher = self.cypher_agent.generate(
                question,
                schema
            )

            print("=" * 80)
            print("GENERATED CYPHER")
            print("=" * 80)
            print(cypher)

            # ---------------------------------------------------------
            # Execute Cypher
            # ---------------------------------------------------------

            ##rows = self.query_agent.execute(cypher)
            query_result = self.query_agent.execute(cypher)

            rows = query_result["rows"]

            print("=" * 80)
            print("ROWS RETURNED")
            print("=" * 80)
            print(rows)

            # ---------------------------------------------------------
            # Build Context
            # ---------------------------------------------------------

            if not rows:

                context = "No records found."
                graph = []
            else:
                graph = rows

                context = self.retrieval_agent.rows_to_text(rows)


            print("=" * 80)
            print("CONTEXT")
            print("=" * 80)
            print(context)

            # ---------------------------------------------------------
            # Ask LLM
            # ---------------------------------------------------------

            prompt = f"""
You are an enterprise Knowledge Graph assistant.

Answer ONLY using the Neo4j results below.

If there are no records, clearly state that.

Question
--------
{question}

Cypher Executed
---------------
{cypher}

Neo4j Results
-------------
{context}

Provide a concise business-friendly answer.
"""

            answer = self.llm.generate(prompt)

            return {

                "success": True,

                "question": question,

                "cypher": cypher,

                "rows": rows,

                "graph": graph,

                "answer": answer

            }

        except Exception as ex:

            return {

                "success": False,

                "question": question,

                "error": str(ex)

            }