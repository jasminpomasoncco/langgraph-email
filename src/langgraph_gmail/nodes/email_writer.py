from ..agents import AGENT_REGISTRY
from ..state import GraphState, Email
from ..structured_output import EmailReply


def _get_email_context(state: GraphState) -> tuple[str, str]:
    current_email = state.get("current_email")
    email_category = state.get("email_category")

    if not email_category or not current_email:
        raise ValueError("Missing required email data in the state.")

    body = current_email.body if isinstance(current_email, Email) else ""
    return body, email_category


def _retrieved_context(state: GraphState) -> str:
    messages = state.get("messages") or []
    if not messages:
        return ""
    return getattr(messages[-1], "content", "") or ""


def query_or_email_node(state: GraphState) -> GraphState:
    body, category = _get_email_context(state)

    result = AGENT_REGISTRY["query_or_email"].invoke({
        "email_category": category,
        "email_content": body,
        "context": _retrieved_context(state),
    })

    return {"messages": [result]}


def email_writer_with_context_node(state: GraphState) -> GraphState:
    body, category = _get_email_context(state)

    result = AGENT_REGISTRY["write_email_with_context"].invoke({
        "email_category": category,
        "email_content": body,
        "context": _retrieved_context(state),
    })

    if not isinstance(result, EmailReply):
        raise ValueError("Unexpected result type from email writer chain.")

    original = state["current_email"]
    if not isinstance(original, Email):
        raise ValueError("current_email must be an Email instance.")

    email_response = Email(
        id=original.id,
        subject=result.subject,
        sender=original.sender,
        body=result.body,
        date=original.date,
        message_id=original.message_id,
        references=original.references,
        thread_id=original.thread_id,
    )

    return {"email_response": email_response}
