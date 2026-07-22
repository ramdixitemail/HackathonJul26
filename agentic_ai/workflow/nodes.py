from agents.schema_agent import SchemaAgent
from agents.cypher_agent import CypherAgent
from agents.query_agent import QueryAgent
from agents.retrieval_agent import RetrievalAgent
from llm.ollama_client import OllamaClient

schema = SchemaAgent()
cypher = CypherAgent()
query = QueryAgent()
retrieval = RetrievalAgent()
llm = OllamaClient()

def schema_node(state):

    state["schema"] = schema.get_schema()

    return state

def cypher_node(state):

    state["cypher"] = cypher.generate(

        state["question"],

        state["schema"]

    )

    return state

def query_node(state):

    result = query.execute(state["cypher"])

    state["rows"] = result["rows"]

    return state

def retrieval_node(state):

    state["context"] = retrieval.rows_to_text(

        state["rows"]

    )

    return state

def answer_node(state):

    prompt = f"""
Question

{state['question']}

Context

{state['context']}

Answer only using the context.
"""

    state["answer"] = llm.generate(prompt)

    return state

