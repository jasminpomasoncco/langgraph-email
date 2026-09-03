import os
from functools import lru_cache
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools.retriever import create_retriever_tool
from dotenv import load_dotenv

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
# On Cloud Run the app filesystem is read-only; point this at /tmp there via env.
_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR", str(Path(__file__).resolve().parents[3] / "chroma_db")
)


@lru_cache(maxsize=1)
def get_retriever_tool():
    """Build (once) and return the products/services retriever tool.

    The vector store is created lazily on first use so that importing this
    module stays cheap and free of network calls.
    """
    load_dotenv(override=True)

    txt_files = sorted(_DATA_DIR.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No .txt knowledge files found in {_DATA_DIR}")

    documents = []
    for path in txt_files:
        documents.extend(TextLoader(str(path), encoding="utf-8").load())
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100, chunk_overlap=50
    )
    docs = text_splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        docs, embedding=OpenAIEmbeddings(), persist_directory=_PERSIST_DIR
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    return create_retriever_tool(
        retriever=retriever,
        name="retrieve_products_and_services_information",
        description="Search and return information about products and services.",
    )
