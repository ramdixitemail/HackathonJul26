"""Q&A agent for evidence-based questions."""
from typing import List, Optional
from ..common import (
    QnAQuery, QnAAnswer, Citation, is_mock, lm_complete,
    load_evidence_set, latest_evidence_set
)


class QnAAgent:
    """Agent for answering questions using evidence."""
    
    def answer(self, query: QnAQuery) -> QnAAnswer:
        """
        Answer a question using evidence.
        
        Args:
            query: QnAQuery question
            
        Returns:
            QnAAnswer with citations
        """
        # Load evidence set
        evidence_set = None
        if query.evidence_id:
            evidence_set = load_evidence_set(query.evidence_id)
        elif query.request_id:
            evidence_set = load_evidence_set(query.request_id)
        else:
            evidence_set = latest_evidence_set()
        
        if not evidence_set:
            return QnAAnswer(
                answer="No evidence set found.",
                routed_to="evidence",
                citations=[],
                unsupported=True
            )
        
        # Rank items by relevance to question
        ranked_items = self._rank_items(query.question, evidence_set.items)
        
        # Use top items for answer
        top_items = ranked_items[:4]
        
        if not top_items:
            return QnAAnswer(
                answer="No relevant evidence found for this question.",
                routed_to="evidence",
                citations=[],
                unsupported=True
            )
        
        # Generate answer deterministically in mock mode
        answer_text = self._compose_answer(query.question, top_items)
        
        # Create citations
        citations = []
        for item in top_items:
            citations.append(Citation(
                label=f"{item.id}",
                ref=item.provenance.ref,
                kind="evidence"
            ))
        
        return QnAAnswer(
            answer=answer_text,
            routed_to="evidence",
            citations=citations,
            unsupported=False
        )
    
    def _rank_items(self, question: str, items: List) -> List:
        """Rank items by relevance to question."""
        question_lower = question.lower()
        scored_items = []
        
        for item in items:
            score = 0
            
            # Score based on keyword overlap
            summary_lower = item.summary.lower()
            for word in question_lower.split():
                if len(word) > 3 and word in summary_lower:
                    score += 10
            
            # Score based on type matches
            if any(keyword in question_lower for keyword in ["flow", "trace", "code"]):
                if item.type.value == "code_flow":
                    score += 20
            
            if any(keyword in question_lower for keyword in ["pr", "pull", "approval"]):
                if item.type.value == "pr":
                    score += 20
            
            if any(keyword in question_lower for keyword in ["document", "design", "runbook"]):
                if item.type.value == "doc":
                    score += 20
            
            if any(keyword in question_lower for keyword in ["screenshot", "portal", "compliance"]):
                if item.type.value == "screenshot":
                    score += 20
            
            # Bonus for items mentioning IDs from question
            if any(f"CHG-" in question or f"JIRA-" in question or f"APP-" in question):
                for ap in item.audit_points:
                    if ap in question:
                        score += 15
            
            scored_items.append((score, item))
        
        # Sort by score descending
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_items]
    
    def _compose_answer(self, question: str, items: List) -> str:
        """Compose deterministic answer from items."""
        if is_mock():
            # Deterministic mock answer
            answer_parts = []
            
            # Add summary of evidence
            for item in items:
                if item.type.value == "code_flow":
                    answer_parts.append(f"Code flow trace shows {len(item.flow) if item.flow else 0} steps with all checks passing.")
                elif item.type.value == "pr":
                    answer_parts.append(f"Pull request evidence available with proper approvals.")
                elif item.type.value == "code_snippet":
                    answer_parts.append(f"Code implementation found in {item.provenance.ref}.")
                elif item.type.value == "doc":
                    answer_parts.append(f"Design documentation available: {item.provenance.ref}.")
                elif item.type.value == "screenshot":
                    answer_parts.append(f"Portal compliance screenshot captured for review.")
            
            answer = " ".join(answer_parts) if answer_parts else "Evidence reviewed and supports the audit inquiry."
            
            # Add check results if available
            check_summary = []
            for item in items:
                if item.checks:
                    passed = sum(1 for v in item.checks.values() if v == "PASS")
                    total = len(item.checks)
                    check_summary.append(f"{passed}/{total} checks passed")
            
            if check_summary:
                answer += f" Status: {', '.join(check_summary)}."
            
            return answer
        else:
            # LLM-generated answer
            context = "\n".join([
                f"- {item.id}: {item.summary} (source: {item.provenance.system})"
                for item in items
            ])
            prompt = f"Question: {question}\n\nEvidence:\n{context}\n\nProvide a concise answer based on the evidence."
            return lm_complete(prompt, mock_value="Evidence supports the inquiry.")


if __name__ == "__main__":
    agent = QnAAgent()
    query = QnAQuery(question="What is the evidence for transaction control?")
    answer = agent.answer(query)
    print(f"Q: {query.question}")
    print(f"A: {answer.answer}")
    print(f"Citations: {[c.label for c in answer.citations]}")
