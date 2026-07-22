from typing import TypedDict

class GraphState(TypedDict):

    question: str

    chat_history: list

    selected_entities: list

    last_rows: list

    last_cypher: str

    schema: str

    cypher: str

    rows: list

    context: str

    answer: str