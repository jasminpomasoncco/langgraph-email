from ..agents import AGENT_REGISTRY
from ..state import GraphState, Email

def email_categorizer_node(state: GraphState) -> GraphState:
    body = ""
    email = state.get('current_email')
    if not email:
        state['email_category'] = "No email to categorize"
        return state
    if isinstance(email, Email):
        body = email.body
    result = AGENT_REGISTRY["email_categorizer"].invoke({"email_content": body})
    state['email_category'] = result.category.value
    return state