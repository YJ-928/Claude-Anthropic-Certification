"""
Exercise 01 — Simple MCP Tool

Demonstrates:
- Defining a tool using the @mcp.tool decorator
- Using Field() for parameter descriptions
- Input validation
- Returning structured output

Run with the MCP Inspector:
    mcp dev exercises/exercise_01_simple_tool.py

Or run directly for basic testing:
    python exercises/exercise_01_simple_tool.py
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("ExerciseServer", log_level="ERROR")

# ─── In-memory data store ─────────────────────────────────

notes: dict[str, str] = {
    "shopping": "Buy milk, eggs, and bread",
    "todo": "Finish MCP exercises, review documentation",
    "meeting": "Team standup at 10am, project review at 2pm",
}

# ─── Tool: Read a note ────────────────────────────────────


@mcp.tool(
    name="read_note",
    description="Read the contents of a note by its name.",
)
def read_note(
    note_name: str = Field(description="Name of the note to read"),
) -> str:
    if note_name not in notes:
        raise ValueError(
            f"Note '{note_name}' not found. "
            f"Available notes: {', '.join(notes.keys())}"
        )
    return notes[note_name]


# ─── Tool: Create a note ──────────────────────────────────


@mcp.tool(
    name="create_note",
    description="Create a new note with a name and content.",
)
def create_note(
    note_name: str = Field(description="Name for the new note"),
    content: str = Field(description="Content of the note"),
) -> str:
    if note_name in notes:
        raise ValueError(
            f"Note '{note_name}' already exists. Use edit_note to modify it."
        )
    notes[note_name] = content
    return f"Note '{note_name}' created successfully"


# ─── Tool: List all notes ─────────────────────────────────


@mcp.tool(
    name="list_notes",
    description="List all available note names.",
)
def list_notes() -> str:
    if not notes:
        return "No notes available"
    return ", ".join(notes.keys())


# ─── Entry point ──────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
