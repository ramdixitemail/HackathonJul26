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

