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

---

# Agentic AI Application

The application implements a **multi-agent AI architecture** that combines Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), Knowledge Graphs, and specialized AI agents to answer complex queries and generate audit evidence.

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
HackathonJul26/
├── agents/                          # Main Agentic AI application
│   ├── agents/
│   │   ├── orchestrator.py         # Coordinates multi-agent workflows
│   │   ├── planner.py              # Plans which agents to invoke
│   │   ├── graph_agent.py          # Neo4j Knowledge Graph queries
│   │   ├── rag_agent.py            # Retrieval-Augmented Generation
│   │   ├── sql_agent.py            # SQL database queries
│   │   ├── policy_agent.py         # Policy & compliance agent
│   │   └── utils.py                # Shared utilities
│   │
│   ├── api/                         # REST API endpoints
│   │   ├── routes.py               # Flask/FastAPI route definitions
│   │   └── handlers.py             # Request handlers
│   │
│   ├── llm/
│   │   ├── ollama_client.py        # Ollama LLM client
│   │   └── openai_client.py        # OpenAI API client
│   │
│   ├── models/
│   │   ├── llm.py                  # LLM model configuration
│   │   └── embedding_model.py      # Embedding model initialization
│   │
│   ├── workflow/
│   │   ├── graph_builder.py        # LangGraph workflow builder
│   │   ├── nodes.py                # Workflow node definitions
│   │   ├── router.py               # Request routing logic
│   │   └── state.py                # Workflow state management
│   │
│   ├── prompts/
│   │   ├── system_prompt.txt       # System-level prompts
│   │   ├── orchestrator_prompt.py  # Orchestrator prompts
│   │   ├── agent_prompts.py        # Individual agent prompts
│   │   └── few_shot_examples.py    # Few-shot examples
│   │
│   ├── knowledgegraph/
│   │   ├── neo4j/                  # Neo4j Docker volumes
│   │   ├── import.cypher           # Graph initialization script
│   │   └── queries.py              # Reusable Cypher queries
│   │
│   ├── vectorstore/
│   │   ├── embeddings.py           # Embedding generation
│   │   ├── retrieval.py            # Document retrieval logic
│   │   └── ingestion.py            # Document ingestion pipeline
│   │
│   ├── tools/
│   │   ├── graph_tools.py          # Neo4j query tools
│   │   ├── search_tools.py         # Search and retrieval tools
│   │   ├── sql_tools.py            # Database query tools
│   │   └── external_tools.py       # Third-party integrations
│   │
│   ├── assets/
│   │   ├── logo.png                # Application logo
│   │   └── styles.css              # UI styles
│   │
│   ├── ui/
│   │   ├── app.py                  # Streamlit main app
│   │   ├── pages/                  # Streamlit page modules
│   │   └── components.py           # Reusable UI components
│   │
│   ├── data/
│   │   ├── sample_documents/       # Sample data for RAG
│   │   ├── sample_policies.csv     # Policy templates
│   │   └── knowledge_base/         # Training data
│   │
│   ├── logs/
│   │   └── app.log                 # Application logs
│   │
│   ├── tests/
│   │   ├── test_agents.py          # Agent unit tests
│   │   ├── test_orchestrator.py    # Orchestrator tests
│   │   └── test_workflow.py        # Workflow integration tests
│   │
│   ├── config.py                   # Configuration management
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variable template
│   ├── docker-compose.yml          # Docker services definition
│   ├── Dockerfile                  # Application container image
│   ├── app.py                      # Main application entry point
│   └── README.md                   # Agentic AI module README
│
└── evidencegen/                     # Audit Evidence Generator (complementary module)
    ├── backend/
    │   ├── app.py                  # Flask REST API
    │   ├── templates_config.py     # Control templates
    │   ├── storage.py              # Pack storage logic
    │   ├── agents/                 # Evidence collection agents
    │   │   ├── github_agent.py     # GitHub integration
    │   │   ├── confluence_agent.py # Confluence integration
    │   │   ├── jira_agent.py       # Jira integration
    │   │   ├── approvals_agent.py  # CI/CD pipeline approvals
    │   │   └── screenshots_agent.py # Screenshot capture
    │   └── llm/
    │       ├── llm_client.py       # LLM client
    │       ├── mapping.py          # Evidence-to-requirement mapping
    │       └── qa.py               # Q&A over evidence packs
    │
    ├── frontend/                   # Vanilla HTML/CSS/JS UI
    ├── requirements.txt
    ├── .env.example
    └── run.sh                      # Startup script
```

---

## Module Descriptions

### **agents/** — Core Agentic AI Application

| Subfolder | Purpose |
|-----------|---------|
| **agents/** | Individual AI agents (Orchestrator, Planner, Graph Agent, RAG Agent, SQL Agent, Policy Agent) and shared utilities. |
| **api/** | REST API layer exposing agentic services. |
| **llm/** | LLM client configuration (Ollama, OpenAI). |
| **models/** | LLM and embedding model initialization. |
| **workflow/** | LangGraph workflow definitions, node routing, and state management. |
| **prompts/** | System and agent-specific prompts for LLM interactions. |
| **knowledgegraph/** | Neo4j setup, Cypher scripts, and graph query utilities. |
| **vectorstore/** | Document embedding, ingestion, and semantic retrieval. |
| **tools/** | Specialized tools for graph queries, database searches, and external APIs. |
| **ui/** | Streamlit web interface and UI components. |
| **data/** | Sample documents, policies, and training datasets. |
| **tests/** | Unit and integration tests. |

### **evidencegen/** — Audit Evidence Generator

A complementary module that generates audit evidence packs by collecting evidence from multiple sources (GitHub, Confluence, Jira, CI/CD pipelines) and mapping it against control requirements using an LLM or rule engine.

---

## Agent Workflow

The following sequence illustrates how a user request is processed:

1. User submits a question through the **Web UI** (Streamlit).
2. The **API Layer** receives the request.
3. The **Agent Orchestrator** analyzes the query intent.
4. The **Planner** determines which specialized agents should participate.
5. Selected agents retrieve information from:
   - **Neo4j Knowledge Graph** – Entity relationships
   - **Vector Database (RAG)** – Semantic document search
   - **SQL Databases** – Structured data queries
   - **External APIs** – Third-party integrations
6. Retrieved context is combined and passed to the **LLM**.
7. The **LLM** synthesizes a comprehensive response.
8. The response is returned to the user.

---

## Building and Running the Application

### **Prerequisites**

- Python 3.9+
- Docker and Docker Compose
- Git
- Virtual environment manager (venv or conda)

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/ramdixitemail/HackathonJul26.git
cd HackathonJul26
```

### **Step 2: Set Up Environment Variables**

Copy the example environment file and configure it:

```bash
cp agents/.env.example agents/.env
```

Edit `agents/.env` with your configuration:

```text
# LLM Configuration
OPENAI_API_KEY=<your-openai-api-key>
OLLAMA_HOST=http://localhost:11434
USE_OLLAMA=false

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<your-neo4j-password>

# Vector Store
VECTOR_DB_PATH=./vectorstore
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Application
APP_PORT=8501
API_PORT=8000
LOG_LEVEL=INFO
```

### **Step 3: Start Neo4j and Supporting Services**

Using Docker Compose:

```bash
cd agents
docker-compose up -d neo4j
```

Or manually with Docker:

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/<password> \
  neo4j:5.26
```

Wait for Neo4j to be ready (check `http://localhost:7474`).

### **Step 4: Import Knowledge Graph Data**

```bash
cd agents
docker exec -i neo4j cypher-shell -u neo4j -p <password> < knowledgegraph/import.cypher
```

### **Step 5: Create Python Virtual Environment**

```bash
cd agents
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### **Step 6: Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 7: Run the Application**

#### Option A: Using Streamlit UI (Recommended for Development)

```bash
streamlit run ui/app.py
```

The UI will be available at `http://localhost:8501`.

#### Option B: Using FastAPI (For Production)

```bash
python -m uvicorn api.routes:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000/docs` (Swagger UI).

#### Option C: Using Docker Compose (All Services)

```bash
docker-compose up --build
```

### **Step 8: Verify Setup**

1. **Streamlit UI:** Open `http://localhost:8501` and test with a sample query.
2. **API Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```
3. **Neo4j Browser:** Open `http://localhost:7474` and verify the knowledge graph is loaded.

---

## Configuration

Application settings can be managed through:

1. **Environment Variables** (`.env` file)
2. **config.py** (Python configuration module)
3. **Docker Compose** (service configuration)

Key configuration options:

```python
# config.py
DATABASE_TYPE = "neo4j"  # or "sql"
LLM_PROVIDER = "openai"  # or "ollama"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LOG_LEVEL = "INFO"
MAX_CONTEXT_LENGTH = 4096
AGENT_TIMEOUT = 30  # seconds
```

---

## Supported AI Components

- ✅ Multi-Agent Orchestration
- ✅ Retrieval-Augmented Generation (RAG)
- ✅ Neo4j Knowledge Graph Integration
- ✅ Semantic Search
- ✅ Large Language Models (LLMs) – OpenAI, Ollama
- ✅ Prompt Engineering & Few-shot Learning
- ✅ Context Management
- ✅ Tool Calling & Function Invocation
- ✅ Enterprise Data Retrieval (SQL, APIs)

---

## Technology Stack

| Component | Technology |
|----------|------------|
| **Language** | Python 3.9+ |
| **Web Framework** | Streamlit (UI) / FastAPI (API) |
| **Agent Framework** | LangGraph / LangChain |
| **Knowledge Graph** | Neo4j 5.x |
| **Vector Store** | ChromaDB / FAISS |
| **LLM** | OpenAI GPT / Ollama |
| **Embeddings** | OpenAI / Sentence Transformers |
| **Database** | Neo4j / PostgreSQL (optional) |
| **Containerization** | Docker / Docker Compose |
| **Package Management** | pip / Poetry |
| **Testing** | pytest |
| **Logging** | Python logging / ELK stack (optional) |

---

## Key Features

- ✨ **Multi-agent reasoning and orchestration**
- 🧠 **Knowledge Graph integration using Neo4j**
- 📚 **Retrieval-Augmented Generation (RAG) for contextual answers**
- 🔧 **Modular and extensible agent architecture**
- 🚀 **Enterprise-ready REST API layer**
- 🛠️ **Extensible tool framework for agent capabilities**
- 💬 **Context-aware multi-turn conversations**
- 📄 **Document ingestion and semantic search**
- 🔌 **Pluggable LLM providers (OpenAI, Ollama, etc.)**
- 🐳 **Docker-ready deployment with Compose**
- ✅ **Comprehensive test coverage**
- 📊 **Audit trail and logging**

---

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage report:

```bash
pytest tests/ --cov=. --cov-report=html
```

---

## Troubleshooting

### Neo4j Connection Issues
- Verify Neo4j is running: `docker ps`
- Check credentials in `.env`
- Ensure port 7687 is accessible

### LLM Not Responding
- If using Ollama, ensure it's running: `ollama serve`
- Check `OLLAMA_HOST` environment variable
- Verify API keys for OpenAI

### Module Import Errors
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`

---

## Contributing

1. Create a feature branch: `git checkout -b feature/new-agent`
2. Make your changes and test them
3. Submit a pull request with detailed description

---

## License

This project is part of the HackathonJul26 initiative.

---

## Support & Documentation

- **Neo4j Documentation:** https://neo4j.com/docs/
- **LangChain Documentation:** https://python.langchain.com/
- **Streamlit Documentation:** https://docs.streamlit.io/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
