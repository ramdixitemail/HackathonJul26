from . import llm_client


def answer_question(question, pack):
    """Answer a free-text question about an evidence pack. Uses the LLM if
    configured; otherwise falls back to a simple retrieval-style answer
    built from the pack's evidence and mapping results."""
    evidence = pack.get("evidence", [])
    results = pack.get("mapping_results", [])
    try:
        context_lines = [
            f'- [{e["source_label"]}] {e["title"]}: {e["detail"]} (actor: {e.get("actor")})'
            for e in evidence
        ]
        result_lines = [
            f'- {r.get("requirement_text", r["requirement_id"])}: {r["status"]} — {r["rationale"]}'
            for r in results
        ]
        prompt = (
            "EVIDENCE PACK CONTEXT:\n" + "\n".join(context_lines) +
            "\n\nREQUIREMENT ASSESSMENTS:\n" + "\n".join(result_lines) +
            f"\n\nQUESTION: {question}\n\n"
            "Answer using only the context above. If the context does not contain the "
            "answer, say so plainly. Keep the answer under 120 words."
        )
        text = llm_client.call_llm(prompt, "You are an audit assistant answering questions "
                                            "about a specific evidence pack.")
        if text.strip():
            return text.strip(), "llm:" + llm_client.active_provider()
    except Exception:
        pass

    # Offline fallback: naive keyword match against evidence + results.
    q = question.lower()
    hits = [e for e in evidence if any(w in (e["title"] + e["detail"]).lower()
                                        for w in q.split() if len(w) > 3)]
    if not hits:
        hits = evidence[:3]
    lines = [f'{e["title"]} — {e["detail"]}' for e in hits[:3]]
    body = " ".join(lines) if lines else "No matching evidence was found in this pack."
    return (
        f"(offline mode) Based on the collected evidence: {body}"
    ), "rules"
