    from workflow.graph_builder import graph

class GraphRAGAgent:

    def ask(self, question):

        state = {

            "question": question,

            "schema": "",

            "cypher": "",

            "rows": [],

            "context": "",

            "answer": "",

            "retry_count": 0

        }

        result = graph.invoke(state)

        return {

            "success": True,

            "answer": result["answer"],

            "cypher": result["cypher"],

            "rows": result["rows"],

            "graph": result["rows"]

        }