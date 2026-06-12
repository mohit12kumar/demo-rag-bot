from app.graph.state import StudyState


def memory_node(state: StudyState):

    user_id = state["user_id"]

    # TODO:
    # Fetch from MySQL
    # Fetch holographic memory
    # Fetch weak topics

    state["memory_context"] = [
        {
            "topic": "FastAPI",
            "mastery": 75
        },
        {
            "topic": "Python",
            "mastery": 90
        }
    ]

    return state