from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .graph.email_graph import EmailSupportGraph
from .state import Email

logger = logging.getLogger("langgraph_gmail.api")

app = FastAPI(title="LangGraph Gmail Support", version="0.1.0")

_graph = None

def _get_graph():
    global _graph
    if _graph is None:
        logger.info("compiling email support graph (cold start)")
        _graph = EmailSupportGraph().graph
    return _graph


def _fresh_state() -> dict[str, Any]:
    return {
        "current_email": None,
        "email_category": "",
        "email_response": None,
        "messages": [],
    }


class ProcessResponse(BaseModel):
    handled: bool
    email_category: str | None = None
    email_response: Email | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/process", response_model=ProcessResponse)
def process_latest_email() -> ProcessResponse:
    try:
        final_state = _get_graph().invoke(_fresh_state())
    except Exception as exc:
        logger.exception("graph execution failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    response = final_state.get("email_response")
    return ProcessResponse(
        handled=response is not None,
        email_category=final_state.get("email_category") or None,
        email_response=response,
    )
