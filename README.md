# HackathonJul26
Hackathon Jul 26
# Agentic AI Setup

## Neo4j Knowledge Graph

This project uses **Neo4j** as the Knowledge Graph to store and query relationships between entities.

### 1. Pull and Run Neo4j

Start a Neo4j Docker container with persistent storage.

```bash
docker run -d \
  --name neo4jnew \
  -p 7474:7474 \
  -p 7687:7687 \
  -v d:/dbhackathon/knowledgegraph/neo4j/data:/data \
  -v d:/dbhackathon/knowledgegraph/neo4j/logs:/logs \
  -v d:/dbhackathon/knowledgegraph/neo4j/import:/var/lib/neo4j/import \
  -v d:/dbhackathon/knowledgegraph/neo4j/plugins:/plugins \
  --env NEO4J_AUTH=neo4j/xxxxxx \
  neo4j:5.26
```

Replace `xxxxxx` with your desired Neo4j password.

---

## 2. Import the Knowledge Graph

Once the container is running, import the graph using the supplied Cypher script.

```bash
docker exec -i neo4jnew \
  cypher-shell -u neo4j -p xxxxxx \
  < import.cypher
```

Replace `xxxxxx` with the password configured in the previous step.

---

## 3. Access the Neo4j Browser

Open the Neo4j Browser in your web browser:

```
http://localhost:7474
```

Login using:

- **Username:** `neo4j`
- **Password:** `xxxxxx`

---

## 4. Visualize the Knowledge Graph

Execute the following Cypher query to display the complete graph.

```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]-(m)
RETURN n, r, m;
```

---

## Project Structure

```
knowledgegraph/
├── neo4j/
│   ├── data/
│   ├── logs/
│   ├── import/
│   └── plugins/
└── import.cypher
```

The `import.cypher` file contains the graph schema and data required to initialize the Knowledge Graph.

# Agentic AI Application

The application implements a **multi-agent AI architecture** that combines Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), Knowledge Graphs, and specialized AI agents to answer enterprise and banking-related queries.

The system is designed to be modular, allowing individual agents to collaborate while sharing context through a common orchestration layer.

---

## Architecture Overview

The application consists of the following major components:

- **Web UI** – User interface for interacting with the AI assistant.
- **API Layer** – Receives requests and coordinates execution.
- **Agent Orchestrator** – Determines which agent(s) should handle a request.
- **Knowledge Graph (Neo4j)** – Stores business entities and their relationships.
- **Vector Database / RAG** – Retrieves relevant documents and embeddings.
- **LLM** – Performs reasoning and response generation.
- **Specialized Agents** – Domain-specific agents for answering user queries.

---

## Folder Structure

```
agents/
│
├── api/
│   ├── app.py
│   ├── routes.py
│   └── config.py
│
├── agents/
│   ├── orchestrator.py
│   ├── planner.py
│   ├── graph_agent.py
│   ├── rag_agent.py
│   ├── sql_agent.py
│   ├── policy_agent.py
│   └── utils.py
│
├── prompts/
│   ├── system_prompt.txt
│   ├── planner_prompt.txt
│   └── agent_prompts/
│
├── knowledgegraph/
│   ├── neo4j/
│   ├── import.cypher
│   └── graph_loader.py
│
├── vectorstore/
│   ├── embeddings.py
│   ├── ingest.py
│   └── retrieval.py
│
├── models/
│   ├── llm.py
│   └── embedding_model.py
│
├── tools/
│   ├── graph_tools.py
│   ├── search_tools.py
│   └── utility_tools.py
│
├── ui/
│   ├── static/
│   ├── templates/
│   └── app.py
│
├── data/
│   ├── documents/
│   ├── csv/
│   └── sample_data/
│
├── logs/
│
├── tests/
│
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## Folder Description

| Folder | Description |
|---------|-------------|
| **api/** | REST APIs that expose the Agentic AI services. |
| **agents/** | Contains the individual AI agents and the orchestration logic responsible for coordinating them. |
| **prompts/** | System prompts and agent-specific prompts used for LLM interactions. |
| **knowledgegraph/** | Neo4j-related scripts, Cypher files, and graph loading utilities. |
| **vectorstore/** | Document ingestion, embedding generation, and semantic retrieval logic. |
| **models/** | LLM configuration and embedding model initialization. |
| **tools/** | Helper tools that agents invoke, including graph queries and document retrieval. |
| **ui/** | Web application or chatbot interface. |
| **data/** | Source documents, CSV files, and sample datasets. |
| **logs/** | Application logs. |
| **tests/** | Unit and integration tests. |

---

## Agent Workflow

The following sequence illustrates how a user request is processed:

1. User submits a question through the Web UI.
2. The API receives the request.
3. The Agent Orchestrator analyzes the query.
4. The Planner determines which specialized agents should participate.
5. The selected agents retrieve information from:
   - Neo4j Knowledge Graph
   - Vector Database (RAG)
   - External tools or APIs (if applicable)
6. Retrieved context is passed to the LLM.
7. The LLM synthesizes a final response.
8. The response is returned to the user.

---

## Running the Application

Install the required dependencies.

```bash
pip install -r requirements.txt
```

Start the application.

```bash
python app.py
```

or, if using FastAPI:

```bash
uvicorn app:app --reload
```

---

## Configuration

Application configuration is managed using environment variables.

Example:

```text
OPENAI_API_KEY=<your-api-key>
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<password>
VECTOR_DB_PATH=./vectorstore
MODEL_NAME=gpt-4.1
```

---

## Supported AI Components

- Multi-Agent Orchestration
- Retrieval-Augmented Generation (RAG)
- Neo4j Knowledge Graph
- Semantic Search
- Large Language Models (LLMs)
- Prompt Engineering
- Context Management
- Tool Calling
- Enterprise Data Retrieval

---

## Technology Stack

| Component | Technology |
|----------|------------|
| Language | Python |
| Web Framework | FastAPI / Flask |
| Knowledge Graph | Neo4j |
| Vector Store | ChromaDB / FAISS |
| LLM | OpenAI GPT / Azure OpenAI |
| Embeddings | OpenAI Embeddings |
| UI | Streamlit / React |
| Containerization | Docker |
| Package Management | pip |

---

## Key Features

- Multi-agent reasoning and orchestration
- Knowledge Graph integration using Neo4j
- Retrieval-Augmented Generation (RAG)
- Modular agent architecture
- Enterprise-ready API layer
- Extensible tool framework
- Context-aware conversations
- Document ingestion and semantic search
- Pluggable LLM providers
- Docker-ready deployment

