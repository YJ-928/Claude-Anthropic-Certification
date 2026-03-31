"""
cli_app.py
==========

Main entry point for the FastMCP Demo Bot.
No API key required.

What this demonstrates:
    - MCP Server exposing tools, resources, and prompts
    - MCP Client connecting to the server over stdio
    - The agentic loop: user input → MockLLM decides → MCP tool executes → answer
    - Resources: read structured data (doc list) from the server
    - Prompts: fetch prompt templates the server has registered

Two ways to interact:

  1. Direct slash commands  (bypass MockLLM, call MCP directly)
     /tools              → list all tools registered on the MCP server
     /resources          → list all resources registered on the MCP server
     /prompts            → list all prompts registered on the MCP server
     /list               → read the docs://documents resource (all doc IDs)
     /read <doc_id>      → call read_doc_contents tool directly
     /edit <id> "a" "b"  → call edit_document tool directly
     /format <doc_id>    → fetch the format prompt template (shows how prompts work)
     /reset              → clear conversation history
     /quit               → exit

  2. Natural language  (routed through the MockLLM agentic loop)
     "read report.pdf"
     "show me what's in financials.docx"
     "edit plan.md \"old text\" \"new text\""
     "@deposition.md"    (mention-style, same as the original app)

Run:
    python cli_app.py
    # or with uv:
    uv run cli_app.py
"""

import asyncio
import sys
import os
import re

from mcp_client import MCPClient
from agent_loop import AgentLoop, _cyan, _green, _yellow, _red, _dim


# ──────────────────────────────────────────────────────────────────────────────
# UI strings
# ──────────────────────────────────────────────────────────────────────────────

DIVIDER = "─" * 58

BANNER = f"""
{_cyan('┌──────────────────────────────────────────────────────────┐')}
{_cyan('│')}   FastMCP Demo Bot  {_dim('· No API Key Required ·')}             {_cyan('│')}
{_cyan('│')}   MCP Server  ←→  MCP Client  ←→  Mock LLM Loop         {_cyan('│')}
{_cyan('└──────────────────────────────────────────────────────────┘')}
  {_yellow('/help')} for all commands  ·  {_yellow('/quit')} to exit
  Or type naturally: {_dim('"read report.pdf"')}  {_dim('"edit plan.md \\"old\\" \\"new\\""')}
"""

HELP = f"""
{_yellow('── Direct commands (call MCP without going through MockLLM) ──')}

  /tools                  List all tools on the MCP server
  /resources              List all resources on the MCP server
  /prompts                List all prompts on the MCP server
  /list                   List all document IDs  (reads docs://documents)
  /read  <doc_id>         Read a document        (calls read_doc_contents)
  /edit  <id> "a" "b"     Edit a document        (calls edit_document)
  /format <doc_id>        Show the format prompt template for a document
  /reset                  Clear conversation history
  /quit                   Exit

{_yellow('── Natural language (routed through MockLLM agentic loop) ──')}

  read report.pdf
  show me financials.docx
  what is in plan.md
  @spec.txt                         (mention-style reference)
  edit outlook.pdf "old" "new"

{_yellow('── How the agentic loop works ──')}

  User input
    → MockLLM.decide(messages, tools)    decides which tool to call
    → MCPClient.call_tool(name, args)    calls the real MCP server
    → MCP server executes the function   returns result
    → MockLLM.decide(messages, tools)    sees result, gives final answer

  With a real API key you would swap MockLLM for Claude/GPT/Gemini.
  The MCP client and server stay exactly the same.
"""


# ──────────────────────────────────────────────────────────────────────────────
# Direct command handlers
# ──────────────────────────────────────────────────────────────────────────────

async def show_tools(client: MCPClient):
    tools = await client.list_tools()
    print(f"\n  {_yellow('MCP Tools')}  ({len(tools)} registered on the server)\n")
    for t in tools:
        print(f"  {_cyan('●')} {_cyan(t.name)}")
        print(f"    {t.description}")
        schema = t.inputSchema
        props  = schema.get("properties", {}) if isinstance(schema, dict) else {}
        req    = set(schema.get("required", [])) if isinstance(schema, dict) else set()
        for param, meta in props.items():
            marker = _red("*") if param in req else " "
            desc   = meta.get("description", "") if isinstance(meta, dict) else ""
            print(f"      {marker} {param}: {desc}")
        print()


async def show_resources(client: MCPClient):
    result   = await client.session().list_resources()
    res_list = result.resources
    print(f"\n  {_yellow('MCP Resources')}  ({len(res_list)} registered on the server)\n")
    for r in res_list:
        print(f"  {_cyan('●')} {_cyan(str(r.uri))}")
        if r.description:
            print(f"    {r.description}")
        if r.mimeType:
            print(_dim(f"    mime: {r.mimeType}"))
        print()


async def show_prompts(client: MCPClient):
    prompts = await client.list_prompts()
    print(f"\n  {_yellow('MCP Prompts')}  ({len(prompts)} registered on the server)\n")
    for p in prompts:
        print(f"  {_cyan('●')} {_cyan(p.name)}: {p.description or ''}")
        if p.arguments:
            for arg in p.arguments:
                req = _red("*") if arg.required else " "
                print(f"      {req} {arg.name}: {arg.description or ''}")
        print()


async def show_doc_list(client: MCPClient):
    print(_dim("\n  [MCP Resource] reading docs://documents …"))
    doc_ids = await client.read_resource("docs://documents")
    print(f"\n  {_yellow('Documents')}  ({len(doc_ids)} available)\n")
    for i, doc_id in enumerate(doc_ids, 1):
        print(f"  {i:2}.  {doc_id}")
    print()


async def read_doc(client: MCPClient, doc_id: str):
    print(_dim(f"\n  [MCP Tool] read_doc_contents(doc_id={doc_id!r}) …"))
    result  = await client.call_tool("read_doc_contents", {"doc_id": doc_id})
    content = _result_to_text(result)
    print(f"\n  {_yellow(doc_id)}\n  {content}\n")


async def edit_doc(client: MCPClient, rest: str):
    """
    Parse: /edit <doc_id> "old text" "new text"
    Also accepts single quotes.
    """
    m = re.match(r'(\S+)\s+["\'](.+?)["\']\s+["\'](.+?)["\']', rest)
    if not m:
        print(_red('  Usage: /edit <doc_id> "old text" "new text"'))
        return
    doc_id, old_str, new_str = m.group(1), m.group(2), m.group(3)
    print(_dim(f"\n  [MCP Tool] edit_document("
               f"doc_id={doc_id!r}, old_str={old_str!r}, new_str={new_str!r}) …"))
    await client.call_tool("edit_document", {
        "doc_id":  doc_id,
        "old_str": old_str,
        "new_str": new_str,
    })
    print(_green(f"  ✓ '{doc_id}' edited: '{old_str}' → '{new_str}'\n"))


async def show_format_prompt(client: MCPClient, doc_id: str):
    """
    Fetches the 'format' prompt template from the MCP server and displays it.
    
    This illustrates how MCP Prompts work:
      - The server defines a prompt template (in mcp_server.py)
      - The client requests it with get_prompt()
      - In the real app, Claude receives this prompt and reformats the document
      - Here we just display what the server would send to an LLM
    """
    print(_dim(f"\n  [MCP Prompt] get_prompt(name='format', doc_id={doc_id!r}) …"))
    messages = await client.get_prompt("format", {"doc_id": doc_id})

    print(f"\n  {_yellow('Prompt template returned by the MCP server:')}")
    print(_dim("  (In the real app, an LLM receives this and rewrites the document)"))
    print(f"  {DIVIDER}")

    for msg in messages:
        role    = getattr(msg, "role", "?").upper()
        content = msg.content
        text    = (
            getattr(content, "text", str(content))
            if not isinstance(content, str)
            else content
        )
        print(f"\n  [{_yellow(role)}]")
        for line in text.strip().splitlines():
            print(f"  {line}")

    print(f"\n  {DIVIDER}\n")


# ──────────────────────────────────────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────────────────────────────────────

def _result_to_text(result) -> str:
    if result is None:
        return "(no result)"
    if hasattr(result, "content"):
        parts = []
        for item in result.content:
            if hasattr(item, "text"):
                parts.append(item.text)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
        return "\n  ".join(parts) or "(empty response)"
    return str(result)


# ──────────────────────────────────────────────────────────────────────────────
# Main — CLI loop
# ──────────────────────────────────────────────────────────────────────────────

async def main():
    print(BANNER)

    # Decide how to launch the MCP server subprocess.
    # Uses the same env-var convention as the original project.
    use_uv  = os.getenv("USE_UV", "0") == "1"
    command = "uv" if use_uv else "python"
    args    = ["run", "mcp_server.py"] if use_uv else ["mcp_server.py"]

    print(f"  {_dim('Starting MCP server and connecting …')}  ", end="", flush=True)

    async with MCPClient(command=command, args=args) as client:
        print(_green("ready.\n"))

        agent = AgentLoop(client, verbose=True)

        while True:
            try:
                raw = input(f"{_cyan('you')} › ").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{_dim('Goodbye.')}")
                break

            if not raw:
                continue

            # ── Parse command vs natural language ────────────────────────────
            if raw.startswith("/"):
                parts = raw.split()
                cmd   = parts[0].lower()

                if cmd in ("/quit", "/exit"):
                    print(_dim("Goodbye."))
                    break

                elif cmd == "/help":
                    print(HELP)

                elif cmd == "/tools":
                    await show_tools(client)

                elif cmd == "/resources":
                    await show_resources(client)

                elif cmd == "/prompts":
                    await show_prompts(client)

                elif cmd == "/list":
                    await show_doc_list(client)

                elif cmd == "/read":
                    if len(parts) < 2:
                        print(_red("  Usage: /read <doc_id>"))
                    else:
                        await read_doc(client, parts[1])

                elif cmd == "/edit":
                    rest = " ".join(parts[1:])
                    await edit_doc(client, rest)

                elif cmd == "/format":
                    if len(parts) < 2:
                        print(_red("  Usage: /format <doc_id>"))
                    else:
                        await show_format_prompt(client, parts[1])

                elif cmd == "/reset":
                    agent.reset()
                    print(_dim("  Conversation history cleared.\n"))

                else:
                    print(_red(f"  Unknown command: {cmd}  (type /help for list)\n"))

            else:
                # ── Natural language → MockLLM agentic loop ──────────────────
                response = await agent.run(raw)
                print(f"\n{_green('bot')} › {response}\n")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
