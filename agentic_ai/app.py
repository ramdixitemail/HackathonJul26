"""
app.py

Enterprise Knowledge Graph Chat UI
Neo4j + Ollama + GraphRAG
"""

import traceback
import streamlit as st

from agents.graphrag_agent import GraphRAGAgent
from config import OLLAMA_MODEL
from PIL import Image
logo = Image.open("assets/logo.png")


# -----------------------------------------------------
# Page Config
# -----------------------------------------------------

st.set_page_config(
    page_title="TEN Twins trust traces...trace trusts TEN Twins..",
    page_icon=logo,
    layout="wide"
)

st.image("assets/logo.png", width=180)

st.markdown("""
<div style="text-align:center">

<h1>
<span style="font-size:70px;color:#0057B8;">T</span>
<span style="font-size:70px;color:#00B8D4;">E</span>
<span style="font-size:70px;color:#6A1B9A;">N</span>
</h1>

<h2 style="margin-top:-35px;">
Trust • Evidences • Nexus
</h2>

<h4 style="color:gray;">
Enterprise Compliance Digital Twins Platform
</h4>

<p style="color:#888;">
Powered by Neo4j • Ollama • LangGraph
</p>

</div>
""", unsafe_allow_html=True)

#st.title("🔍 Trust Evidences Nexus --a compliance digital twins ")
st.caption(f"Neo4j + Ollama ({OLLAMA_MODEL}) + GraphRAG")

# -----------------------------------------------------
# Session State
# -----------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = GraphRAGAgent()

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------

with st.sidebar:

    st.header("Configuration")

    st.success("✅ Neo4j Connected")

    st.success(f"✅ Ollama : {OLLAMA_MODEL}")

    st.divider()

    if st.button("Clear Conversation"):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.subheader("Example Questions")

    st.markdown("""
- Show all applications.

- Show High criticality applications.

- Show applications having vulnerabilities.

- Show vulnerabilities affecting Payment Gateway.

- Show servers hosting Trading applications.

- Show open audit findings.

- Who owns Payment Gateway?

- Which servers have Critical vulnerabilities?

- Show applications deployed on Production servers.

- Summarize audit findings.
""")

# -----------------------------------------------------
# Display Conversation
# -----------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# -----------------------------------------------------
# User Input
# -----------------------------------------------------

question = st.chat_input(
    "Ask a question about your Knowledge Graph..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        with st.spinner("Thinking..."):

            try:

                result = st.session_state.agent.ask(question)

                # -------------------------------------------------
                # Debug View
                # -------------------------------------------------

                with st.expander("Raw Agent Response"):

                    st.json(result)

                # -------------------------------------------------
                # Success
                # -------------------------------------------------

                if result.get("success", False):

                    answer = result.get(
                        "answer",
                        "No answer generated."
                    )

                    cypher = result.get(
                        "cypher",
                        ""
                    )

                    rows = result.get(
                        "rows",
                        []
                    )

                    graph = result.get(
                        "graph",
                        []
                    )

                    placeholder.markdown(answer)

                    with st.expander("Generated Cypher"):

                        st.code(
                            cypher,
                            language="cypher"
                        )

                    with st.expander("Neo4j Results"):

                        st.json(rows)

                    with st.expander("Expanded Graph"):

                        st.json(graph)

                # -------------------------------------------------
                # Failure
                # -------------------------------------------------

                else:

                    answer = result.get(
                        "error",
                        "Unknown Error"
                    )

                    placeholder.error(answer)

            except Exception:

                answer = traceback.format_exc()

                placeholder.code(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )