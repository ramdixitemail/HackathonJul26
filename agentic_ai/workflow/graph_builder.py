from langgraph.graph import StateGraph

from workflow.state import GraphState

from workflow.nodes import *

from workflow.router import *

builder = StateGraph(GraphState)

builder.add_node("schema", schema_node)

builder.add_node("cypher", cypher_node)

builder.add_node("query", query_node)

builder.add_node("retrieve", retrieval_node)

builder.add_node("answer", answer_node)

builder.set_entry_point("schema")

builder.add_edge("schema","cypher")

builder.add_edge("cypher","query")

builder.add_edge("query","retrieve")

builder.add_edge("retrieve","answer")

builder.set_finish_point("answer")

graph = builder.compile()

