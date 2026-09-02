from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class Email(BaseModel):
    id: str = Field(..., description="The unique identifier of the email")
    subject: str = Field(..., description="The subject of the email")
    sender: str = Field(..., description="The sender of the email")
    body: str = Field(..., description="The body content of the email")
    date: str = Field(..., description="The date the email was sent")

class GraphState(TypedDict):
    current_email: Email | None
    email_category: str
