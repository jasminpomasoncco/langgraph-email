from ..state import GraphState, Email
from ..utils.gmail_utils import get_most_recent_email


def listen_for_emails_node(state: GraphState) -> GraphState:
    recent_email = get_most_recent_email()
    if recent_email:
        state['current_email'] = Email(**recent_email)
    return state