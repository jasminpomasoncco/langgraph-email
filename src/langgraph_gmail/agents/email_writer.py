from ..utils.rag_utils import get_retriever_tool
from ..prompts import EMAIL_WRITER_PROMPT
from ..structured_output import EmailReply
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


def _create_email_writer_chain(use_rag: bool, use_structured_output: bool):
    llm = ChatOpenAI(model="gpt-4o-mini")

    if use_rag:
        llm = llm.bind_tools([get_retriever_tool()])

    if use_structured_output:
        llm = llm.with_structured_output(EmailReply)

    email_writer_prompt_template = PromptTemplate(
        input_variables=["email_category", "email_content", "context"],
        template=EMAIL_WRITER_PROMPT,
    )

    return email_writer_prompt_template | llm


def query_or_email():
    return _create_email_writer_chain(use_rag=True, use_structured_output=False)


def write_email_with_context():
    return _create_email_writer_chain(use_rag=False, use_structured_output=True)
