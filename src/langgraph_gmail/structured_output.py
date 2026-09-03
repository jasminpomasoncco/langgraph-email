from pydantic import BaseModel, Field
from enum import Enum

class EmailCategory(str, Enum):
    product_enquiry = "product_enquiry"
    customer_complaint = "customer_complaint"
    customer_feedback = "customer_feedback"
    unrelated = "unrelated"
    
class CategorizedEmailOutput(BaseModel):
    category: EmailCategory = Field(..., description="The detected category of the email")


class EmailReply(BaseModel):
    """The part of a reply email that the LLM is responsible for writing."""

    subject: str = Field(..., description="Subject line of the reply, starting with 'Re:'")
    body: str = Field(..., description="Body content of the reply email, written in Spanish")