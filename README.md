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

The application implements a **multi-agent AI architecture** that combines Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), Knowledge Graphs, and specialized AI agents to answer complex queries.

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
agentic_ai/
├── agents/                          # Individual AI agents and utilities
├── api/                             # REST API endpoints (if present)
├── llm/                             # LLM client configuration
├── workflow/                        # LangGraph workflow definitions
├── prompts/                         # System and agent-specific prompts
├── graph/                           # Neo4j knowledge graph utilities
├── imports/                         # Import scripts and data
├── assets/                          # Application assets (logo, styles)
├── logs/                            # Application logs
├── app.py                           # Main application entry point
├── config.py                        # Configuration management
├── requirements.txt                 # Python dependencies
└── .env                             # Environment variables
```

---

## Module Descriptions

| Folder | Purpose |
|--------|---------|
| **agents/** | Individual AI agents and shared utilities for multi-agent orchestration. |
| **api/** | REST API layer exposing agentic services (optional). |
| **llm/** | LLM client configuration (Ollama, OpenAI). |
| **workflow/** | LangGraph workflow definitions and node routing. |
| **prompts/** | System and agent-specific prompts for LLM interactions. |
| **graph/** | Neo4j utilities and Cypher query helpers. |
| **imports/** | Import scripts and initialization data. |
| **assets/** | Static assets for the UI (logo, styles, etc.). |
| **logs/** | Application logs directory. |

---

## Agent Workflow

The following sequence illustrates how a user request is processed:

1. User submits a question through the **Web UI** or **API**.
2. The **Workflow Layer** receives the request.
3. The **Agent Orchestrator** analyzes the query intent.
4. Selected agents retrieve information from:
   - **Neo4j Knowledge Graph** – Entity relationships
   - **Vector Database (RAG)** – Semantic document search
   - **External APIs** – Third-party integrations
5. Retrieved context is combined and passed to the **LLM**.
6. The **LLM** synthesizes a comprehensive response.
7. The response is returned to the user.

---

## Building and Running the Application

### **Prerequisites**

- Python 3.9+
- Docker (for Neo4j)
- Git
- Virtual environment manager (venv or conda)

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/ramdixitemail/HackathonJul26.git
cd HackathonJul26
```

### **Step 2: Set Up Environment Variables**

Navigate to the agentic_ai directory and configure your environment:

```bash
cd agentic_ai
cat .env
```

Edit `agentic_ai/.env` with your configuration:

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

Using Docker:

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
cd agentic_ai/imports
docker exec -i neo4j cypher-shell -u neo4j -p <password> < import.cypher
```

### **Step 5: Create Python Virtual Environment**

```bash
cd agentic_ai
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

```bash
python app.py
```

The application will start and be accessible based on the configuration in your `.env` file.

### **Step 8: Verify Setup**

1. **Application:** Verify it's running on the configured port.
2. **Neo4j Browser:** Open `http://localhost:7474` and verify the knowledge graph is loaded.

---

## Configuration

Application settings can be managed through:

1. **Environment Variables** (`.env` file)
2. **config.py** (Python configuration module)

Key configuration options in `.env`:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<password>
OPENAI_API_KEY=<api-key>
USE_OLLAMA=false
OLLAMA_HOST=http://localhost:11434
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

---

## Technology Stack

| Component | Technology |
|----------|------------|
| **Language** | Python 3.9+ |
| **Agent Framework** | LangGraph / LangChain |
| **Knowledge Graph** | Neo4j 5.x |
| **LLM** | OpenAI GPT / Ollama |
| **Embeddings** | OpenAI / Sentence Transformers |
| **Containerization** | Docker |
| **Package Management** | pip |

---

## Key Features

- ✨ **Multi-agent reasoning and orchestration**
- 🧠 **Knowledge Graph integration using Neo4j**
- 📚 **Retrieval-Augmented Generation (RAG) for contextual answers**
- 🔧 **Modular and extensible agent architecture**
- 🚀 **Enterprise-ready REST API layer (optional)**
- 💬 **Context-aware interactions**
- 🔌 **Pluggable LLM providers (OpenAI, Ollama, etc.)**

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
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
