from pydantic import BaseModel, Field
from enum import Enum

class EmailCategory(str, Enum):
    product_enquiry = "product_enquiry"
    customer_complaint = "customer_complaint"
    customer_feedback = "customer_feedback"
    unrelated = "unrelated"
    
class CategorizedEmailOutput(BaseModel):
    category: EmailCategory = Field(..., description="The detected category of the email")