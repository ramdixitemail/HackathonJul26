"""Router for Q&A queries."""
from ..common import QnAQuery, QnAAnswer, Citation
from .agent import QnAAgent
from ..graph_agent.agent import GraphAgent


GRAPH_WORDS = {
    'sii', 'vulnerability', 'cve', 'remediation', 'application',
    'overdue', 'past_due', 'portfolio', 'audit_item', 'on_track', 'at_risk',
    'critical', 'high', 'medium', 'low', 'risk'
}

EVIDENCE_WORDS = {
    'ev-', 'evidence', 'dblink', 'pr', 'pull_request', 'snippet',
    'screenshot', 'commit', 'approval', 'flow', 'transaction_control',
    'design', 'document', 'approval', 'code', 'trace'
}


def route(query: QnAQuery) -> QnAAnswer:
    """
    Route query to appropriate agent.
    
    Args:
        query: QnAQuery
        
    Returns:
        QnAAnswer from routed agent
    """
    qna_agent = QnAAgent()
    graph_agent = GraphAgent()
    
    # Determine scope
    if query.scope != "auto":
        if query.scope == "evidence":
            answer = qna_agent.answer(query)
            answer.routed_to = "evidence"
            return answer
        elif query.scope == "graph":
            answer = graph_agent.answer(query.question)
            answer_obj = QnAAnswer(
                answer=answer.narrative,
                routed_to="graph",
                citations=[Citation(label=path, ref="", kind="graph") for path in answer.cited_paths],
                table=answer.table
            )
            return answer_obj
    
    # Auto-routing: score question for graph vs evidence keywords
    question_lower = query.question.lower()
    words = question_lower.split()
    
    graph_score = sum(1 for word in words if any(g in word for g in GRAPH_WORDS))
    evidence_score = sum(1 for word in words if any(e in word for e in EVIDENCE_WORDS))
    
    # If evidence mentioned in question
    if query.evidence_id or query.request_id:
        answer = qna_agent.answer(query)
        answer.routed_to = "evidence"
        return answer
    
    # Route based on scoring
    if graph_score > evidence_score and graph_score > 0:
        # Graph query
        answer = graph_agent.answer(query.question)
        answer_obj = QnAAnswer(
            answer=answer.narrative,
            routed_to="graph",
            citations=[Citation(label=path, ref="", kind="graph") for path in answer.cited_paths],
            table=answer.table
        )
        return answer_obj
    elif evidence_score > 0 or graph_score == 0:
        # Evidence query (default)
        answer = qna_agent.answer(query)
        answer.routed_to = "evidence"
        return answer
    else:
        # Both scored equally - combine
        evidence_answer = qna_agent.answer(query)
        graph_answer = graph_agent.answer(query.question)
        
        # Merge answers
        combined_answer = f"{evidence_answer.answer}\n\nAdditional context from knowledge graph: {graph_answer.narrative}"
        
        citations = evidence_answer.citations + [
            Citation(label=path, ref="", kind="graph") for path in graph_answer.cited_paths
        ]
        
        return QnAAnswer(
            answer=combined_answer,
            routed_to="blended",
            citations=citations,
            table=graph_answer.table if not evidence_answer.table else evidence_answer.table
        )


if __name__ == "__main__":
    # Test evidence routing
    query1 = QnAQuery(question="What evidence do we have for transaction control?")
    answer1 = route(query1)
    print(f"Q1: {query1.question}")
    print(f"Routed to: {answer1.routed_to}")
    print(f"A1: {answer1.answer}\n")
    
    # Test graph routing
    query2 = QnAQuery(question="What are the high-severity SIIs past due?")
    answer2 = route(query2)
    print(f"Q2: {query2.question}")
    print(f"Routed to: {answer2.routed_to}")
    print(f"A2: {answer2.answer}\n")
