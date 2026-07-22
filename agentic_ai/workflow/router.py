def should_retry(state):

    if len(state["rows"]) == 0:

        return "retry"

    return "answer"