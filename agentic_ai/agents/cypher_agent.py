"""
cypher_agent.py

Uses Ollama to convert natural language into Cypher.
"""

from llm.ollama_client import OllamaClient
import re

class CypherAgent:

    def __init__(self):

        self.llm = OllamaClient()

    # -------------------------------------------------------

    def clean_cypher(self, text: str) -> str:
        # Remove markdown fences
        text = text.replace("```cypher", "").replace("```", "")

        # Find the first Cypher keyword
        pattern = re.compile(
            r"(MATCH|OPTIONAL MATCH|CALL|WITH|UNWIND|MERGE|CREATE|RETURN).*",
            re.IGNORECASE | re.DOTALL,
        )

        match = pattern.search(text)

        if not match:
            raise ValueError("No Cypher statement found in LLM response.")

        cypher = match.group(0)

        # Remove explanatory text after the query
        stop_phrases = [
            "\nThis query",
            "\nExplanation",
            "\nThe query",
            "\nHere",
        ]

        for phrase in stop_phrases:
            idx = cypher.find(phrase)
            if idx != -1:
                cypher = cypher[:idx]

        return cypher.strip()

    def generate(
        self,
        question,
        schema
    ):

        prompt = f"""
You are neo4j and cypher language expert 

Use ONLY the labels, properties, and relationship directions listed below.

Do NOT invent labels or relationships.

If the graph contains:

Do not load or delete any data from neo4j

(Application)-[:OWNED_BY]->(Owner)
 
you MUST use that direction.

Do not explain anything.

show the cypher you have generated and show the result as well
Knowledge Graph Schema

The graph may require traversing multiple relationships.

Never assume there is a direct relationship between two labels.

Always use the graph topology below.

If multiple hops are required, traverse through the intermediate nodes.

Example:

Question:
Show applications with vulnerabilities

Correct Cypher:

MATCH (a:Application)-[:DEPLOYED_ON]->(s:Server)-[:HAS_VULNERABILITY]->(v:Vulnerability)
RETURN DISTINCT a.name

Generate ONLY executable Cypher.

Rules:

1. Variables MUST always be declared in MATCH.

2. Never introduce variables in RETURN.

3. Never create nodes.

4. Never create relationships.

5. Never use pattern expressions inside RETURN.

6. Use only labels and relationships from the schema.

7. If owner information is requested, always MATCH the Owner node.

Bad Example

MATCH (a:Application)
RETURN a.name,(o:Owner)-[:OWNED_BY]->(a)

Good Example

MATCH (a:Application)-[:OWNED_BY]->(o:Owner)
RETURN a.name,o.name

Return ONLY Cypher.

No explanation.

No markdown.

No comments.
  
example question and equivalent cyper queries
Question

Show all applications

Cypher

MATCH (a:Application)
RETURN a

--------------------------------

Question

Show all servers

Cypher

MATCH (s:Server)
RETURN s

--------------------------------

Question

Show vulnerabilities

Cypher

MATCH (v:Vulnerability)
RETURN v

--------------------------------

Question

Show owners

Cypher

MATCH (o:Owner)
RETURN o

{schema}

Question

{question}
"""

        response = self.llm.generate(prompt)
        cypher = self.clean_cypher(response)

        cypher = cypher.replace("```cypher", "")
        cypher = cypher.replace("```", "")
        cypher = cypher.strip()

        return cypher