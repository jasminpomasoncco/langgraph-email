from ..prompts import EMAIL_CATEGORIZER_PROMPT
from ..structured_output import CategorizedEmailOutput
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv(override=True)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def categorize_email() -> CategorizedEmailOutput:
    email_categorizer_prompt = PromptTemplate(
        template=EMAIL_CATEGORIZER_PROMPT,
        input_variables=["email_content"]
    )
    return email_categorizer_prompt | llm.with_structured_output(CategorizedEmailOutput)

