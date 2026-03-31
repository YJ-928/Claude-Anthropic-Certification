"""
agent_loop.py
=============

Implements the MCP agentic loop WITHOUT a real LLM API.

In the original course project (core/chat.py), the loop is:

    while True:
        response = claude.chat(messages, tools=mcp_tools)      ← API call
        if response.stop_reason == "tool_use":
            execute tools via MCP client
            add results to messages
        else:
            return response.text                               ← done

This file does the EXACT same loop, replacing the Claude API call
with MockLLM.decide(). The MCP client and server are real and unchanged.

What you can observe running this:
    - MockLLM reads messages + available tools, returns a decision
    - AgentLoop calls the MCP tool via the real MCP client
    - MCP server executes the function and returns a result
    - Loop continues until MockLLM gives a FinalAnswerDecision
"""

import json
from mcp_client import MCPClient
from mock_llm import MockLLM, ToolCallDecision, FinalAnswerDecision


# ──────────────────────────────────────────────────────────────────────────────
# ANSI colour helpers (no dependencies needed)
# ──────────────────────────────────────────────────────────────────────────────

def _dim(text: str)    -> str: return f"\033[2;37m{text}\033[0m"
def _cyan(text: str)   -> str: return f"\033[96m{text}\033[0m"
def _green(text: str)  -> str: return f"\033[92m{text}\033[0m"
def _yellow(text: str) -> str: return f"\033[93m{text}\033[0m"
def _red(text: str)    -> str: return f"\033[91m{text}\033[0m"


# ──────────────────────────────────────────────────────────────────────────────
# AgentLoop
# ──────────────────────────────────────────────────────────────────────────────

class AgentLoop:
    """
    Orchestrates the agentic loop: MockLLM ↔ MCP Client ↔ MCP Server.

    Architecture (identical to the original course project):

        AgentLoop  ←→  MockLLM       (decides what to do — was: Claude API)
        AgentLoop  ←→  MCPClient     (executes tool calls — unchanged)
        MCPClient  ←→  MCP Server    (runs the actual tools — unchanged)

    Usage:
        loop = AgentLoop(client)
        response = await loop.run("read report.pdf")
        print(response)

    The loop keeps conversation history in self.messages across calls,
    so follow-up questions have context (same as the original app).
    Call loop.reset() to start a fresh conversation.
    """

    # Safety cap: how many tool-call → result cycles before we stop
    MAX_TURNS = 6

    def __init__(self, client: MCPClient, verbose: bool = True):
        """
        Args:
            client:  Connected MCPClient instance
            verbose: If True, print MockLLM thinking and tool call details
        """
        self.client  = client
        self.llm     = MockLLM()
        self.verbose = verbose
        self.messages: list = []

    def reset(self):
        """Clear conversation history."""
        self.messages = []

    async def run(self, user_input: str) -> str:
        """
        Process one user turn through the full agentic loop.

        Steps (mirrors core/chat.py exactly):
            1. Append user message to self.messages
            2. Fetch available tools from MCP server
            3. Ask MockLLM to decide: tool_call or final_answer?
            4a. If tool_call  → call tool via MCP, add result, go to 3
            4b. If final_answer → append assistant message, return text

        Returns:
            Final text response string.
        """
        # Step 1: add user turn
        self.messages.append({"role": "user", "content": user_input})

        # Step 2: get live tool list from MCP server
        available_tools = await self._fetch_tools()

        for turn in range(self.MAX_TURNS):
            # Step 3: MockLLM decides
            decision = self.llm.decide(self.messages, available_tools)

            if self.verbose and decision.thinking:
                print(_dim(f"  [MockLLM] {decision.thinking}"))

            # Step 4b: LLM is done → return final answer
            if isinstance(decision, FinalAnswerDecision):
                self.messages.append({
                    "role": "assistant",
                    "content": decision.content,
                })
                return decision.content

            # Step 4a: LLM wants to call a tool
            if isinstance(decision, ToolCallDecision):
                await self._execute_tool(decision, turn)
                # Loop continues — MockLLM will see the tool result next turn

        return "Reached maximum loop depth without a final answer."

    # ──────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────────

    async def _execute_tool(self, decision: ToolCallDecision, turn: int):
        """
        Call the MCP tool and add the result into self.messages.

        The result is added as a user message containing a tool_result block —
        the exact same format the original chat.py uses for Claude.
        """
        if self.verbose:
            args_pretty = json.dumps(decision.tool_args, indent=4)
            print(_cyan(f"  → Calling MCP tool: {decision.tool_name}"))
            print(_dim(  f"    args: {args_pretty}"))

        try:
            result   = await self.client.call_tool(decision.tool_name, decision.tool_args)
            text_out = _extract_text(result)

            if self.verbose:
                preview = text_out[:80] + "…" if len(text_out) > 80 else text_out
                print(_green(f"  ← Tool result: {preview!r}"))

            # Add tool result as a user message (agentic loop pattern)
            self.messages.append({
                "role": "user",
                "content": [{
                    "type":        "tool_result",
                    "tool_use_id": f"mock_tool_{turn}",
                    "content":     text_out,
                    "is_error":    False,
                }],
            })

        except Exception as exc:
            error_msg = str(exc)
            if self.verbose:
                print(_red(f"  ✗ Tool error: {error_msg}"))

            self.messages.append({
                "role": "user",
                "content": [{
                    "type":        "tool_result",
                    "tool_use_id": f"mock_tool_{turn}",
                    "content":     error_msg,
                    "is_error":    True,
                }],
            })

    async def _fetch_tools(self) -> list[dict]:
        """Fetch current tool list from MCP server and normalise to dicts."""
        tools = await self.client.list_tools()
        return [
            {
                "name":         t.name,
                "description":  t.description,
                "input_schema": t.inputSchema,
            }
            for t in tools
        ]


# ──────────────────────────────────────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────────────────────────────────────

def _extract_text(result) -> str:
    """Pull plain text out of a CallToolResult object."""
    if result is None:
        return ""
    if hasattr(result, "content"):
        parts = []
        for item in result.content:
            if hasattr(item, "text"):
                parts.append(item.text)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
        return "\n".join(parts)
    return str(result)
