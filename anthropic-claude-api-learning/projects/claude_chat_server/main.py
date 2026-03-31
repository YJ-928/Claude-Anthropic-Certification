"""
main.py — FastAPI chat server with session management and SSE streaming.

Endpoints:
  POST /sessions                    → create a new session, returns session_id
  DELETE /sessions/{session_id}     → delete a session
  GET  /sessions                    → list all active session IDs

  POST /chat                        → send a message, receive full JSON reply
  POST /chat/stream                 → send a message, receive SSE stream

Run:
    uvicorn projects.claude_chat_server.main:app --reload
  or from inside this directory:
    uvicorn main:app --host 127.0.0.1 --port 8000 --reload
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

from .chat_service import service
from .streaming import sse_generator
from . import config

app = FastAPI(
    title="Claude Chat Server",
    description="Multi-session chat API powered by Anthropic Claude.",
    version="1.0.0",
)


# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="ID of an existing session.")
    message: str    = Field(..., description="User message text.")
    model: Optional[str]      = Field(None, description="Override the default model.")
    max_tokens: Optional[int] = Field(None, description="Override max_tokens.")


class ChatResponse(BaseModel):
    session_id: str
    reply: str


class SessionResponse(BaseModel):
    session_id: str


# ── Session endpoints ─────────────────────────────────────────────────────────

@app.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session():
    """Create a new chat session."""
    session_id = service.create_session()
    return SessionResponse(session_id=session_id)


@app.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: str):
    """Delete a session and its history."""
    if session_id not in service.list_sessions():
        raise HTTPException(status_code=404, detail="Session not found.")
    service.clear_session(session_id)


@app.get("/sessions")
def list_sessions():
    """List all active session IDs."""
    return {"sessions": service.list_sessions()}


# ── Chat endpoints ────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Send a message and receive the full reply synchronously."""
    try:
        reply = service.send_message(
            req.session_id,
            req.message,
            model=req.model,
            max_tokens=req.max_tokens,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return ChatResponse(session_id=req.session_id, reply=reply)


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    """Send a message and receive the reply as a Server-Sent Events stream."""
    if req.session_id not in service.list_sessions():
        raise HTTPException(status_code=404, detail="Session not found.")

    chunks = service.get_stream(
        req.session_id,
        req.message,
        model=req.model,
        max_tokens=req.max_tokens,
    )
    return StreamingResponse(
        sse_generator(chunks),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model": config.DEFAULT_MODEL}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
