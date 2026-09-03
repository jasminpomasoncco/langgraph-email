from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class Email(BaseModel):
    id: str = Field(..., description="The unique identifier of the email")
    subject: str = Field(..., description="The subject of the email")
    sender: str = Field(..., description="The sender of the email")
    body: str = Field(..., description="The body content of the email")
    date: str = Field(..., description="The date the email was sent")
    message_id: str = Field(..., description="The message ID of the email") 
    references: str = Field(..., description="The references of the email")
    thread_id: str = Field(..., description="The thread ID of the email")

class GraphState(TypedDict):
    current_email: Email | None
    email_category: str
    email_response: Email | None
    messages: Annotated[list[AnyMessage], add_messages]
