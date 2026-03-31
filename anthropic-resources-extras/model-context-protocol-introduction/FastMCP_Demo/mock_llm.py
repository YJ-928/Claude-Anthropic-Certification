"""
mock_llm.py
===========

Replaces the Claude API (core/claude.py) in the agentic loop.

In the original course project the flow is:
    User message
        → Claude API called with messages + available MCP tools
        → Claude returns stop_reason="tool_use"  → execute tool → loop back
        → Claude returns stop_reason="end_turn"  → final answer

This module does the SAME loop but without an API key.
MockLLM is a rule-based engine that:
    1. Reads the conversation messages (same format Claude receives)
    2. Decides which MCP tool to call — or returns a final answer
    3. After a tool result arrives, synthesises a readable response

Because the interface is identical to what chat.py/agent_loop.py expects,
you can swap MockLLM out for a real LLM (Claude, GPT, Gemini) later with
minimal changes.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# Decision types — mirror what an LLM API would return
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ToolCallDecision:
    """
    The mock LLM has decided to call an MCP tool.

    Equivalent to Claude returning stop_reason="tool_use".
    """
    type: str = "tool_call"
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)
    # thinking shows the "reasoning" — displayed in the CLI for learning purposes
    thinking: str = ""


@dataclass
class FinalAnswerDecision:
    """
    The mock LLM has a final text answer ready.

    Equivalent to Claude returning stop_reason="end_turn".
    """
    type: str = "final_answer"
    content: str = ""
    thinking: str = ""


# Union type for type hints
Decision = ToolCallDecision | FinalAnswerDecision


# ──────────────────────────────────────────────────────────────────────────────
# MockLLM
# ──────────────────────────────────────────────────────────────────────────────

class MockLLM:
    """
    A stateless, rule-based simulation of an LLM in the MCP agentic loop.

    Stateless means: it holds NO conversation history itself. The caller
    (AgentLoop) manages the messages list and passes the full history on
    every call — exactly how a real LLM API works.

    How to use:
        llm = MockLLM()
        decision = llm.decide(messages, available_tools)

        if isinstance(decision, ToolCallDecision):
            # execute decision.tool_name with decision.tool_args via MCP client
            # add tool result to messages
            # call llm.decide() again (the loop)

        elif isinstance(decision, FinalAnswerDecision):
            # show decision.content to the user
            # loop ends
    """

    def decide(self, messages: list, available_tools: list[dict]) -> Decision:
        """
        Core method — called on every turn of the agentic loop.

        Args:
            messages:        Full conversation history.
                             Each entry: {"role": "user"|"assistant", "content": str | list}
                             Tool results are added as user messages with list content.
            available_tools: Tools reported by the MCP server.
                             Each: {"name": str, "description": str, "input_schema": dict}

        Returns:
            ToolCallDecision  — call this tool then loop back
            FinalAnswerDecision — done, show this to the user
        """
        if not messages:
            return FinalAnswerDecision(
                content="No input received.",
                thinking="Empty messages list — nothing to process.",
            )

        # ── Turn 2+: last message is a tool result → synthesise final answer ──
        last = messages[-1]
        if last["role"] == "user" and isinstance(last["content"], list):
            return self._answer_from_tool_result(last["content"])

        # ── Turn 1: parse the user's natural language input ──
        user_text = self._latest_user_text(messages)
        tool_names = {t["name"] for t in available_tools}
        return self._route_to_tool(user_text, tool_names)

    # ──────────────────────────────────────────────────────────────────────────
    # Private: intent routing (the "brain")
    # ──────────────────────────────────────────────────────────────────────────

    def _route_to_tool(self, text: str, tool_names: set) -> Decision:
        """
        Match the user's text against known intent patterns.
        Returns a ToolCallDecision if a tool should be called,
        or FinalAnswerDecision if we can't determine an action.
        """

        # ── Intent: edit_document ─────────────────────────────────────────────
        # Patterns supported:
        #   edit report.pdf "20m" "30m"
        #   edit report.pdf "20m" to "30m"
        #   change/update report.pdf "20m" with "30m"
        edit_match = re.search(
            r'(?:edit|change|update|replace)\s+(\S+\.\S+)\s+'
            r'["\'](.+?)["\']\s+(?:to|with|->|→)?\s*["\'](.+?)["\']',
            text, re.IGNORECASE,
        )
        if edit_match and "edit_document" in tool_names:
            doc_id  = edit_match.group(1)
            old_str = edit_match.group(2)
            new_str = edit_match.group(3)
            return ToolCallDecision(
                tool_name="edit_document",
                tool_args={"doc_id": doc_id, "old_str": old_str, "new_str": new_str},
                thinking=(
                    f"User wants to edit '{doc_id}': "
                    f"replace '{old_str}' with '{new_str}'. "
                    f"Calling edit_document tool."
                ),
            )

        # ── Intent: read_doc_contents ─────────────────────────────────────────
        # Patterns supported:
        #   read report.pdf
        #   show me financials.docx
        #   what's in plan.md / what is in plan.md
        #   contents of spec.txt
        #   @deposition.md  (mention style from the original app)
        read_match = re.search(
            r'(?:read|show|open|get|fetch|display|contents?\s+of'
            r'|what(?:\'s|\s+is)\s+in|tell me about)\s+(?:\w+\s+)*(\S+\.\S+)',
            text, re.IGNORECASE,
        )
        if not read_match:
            # @mention style: @report.pdf
            read_match = re.search(r'@(\S+\.\S+)', text)

        if read_match and "read_doc_contents" in tool_names:
            doc_id = read_match.group(1)
            return ToolCallDecision(
                tool_name="read_doc_contents",
                tool_args={"doc_id": doc_id},
                thinking=(
                    f"User wants to read '{doc_id}'. "
                    f"Calling read_doc_contents tool."
                ),
            )

        # ── No clear tool intent ──────────────────────────────────────────────
        return FinalAnswerDecision(
            content=(
                "I couldn't determine which action to take.\n"
                "  Try: 'read <doc_id>'  |  'edit <doc_id> \"old\" \"new\"'\n"
                "  Or type '/help' to see all available commands."
            ),
            thinking="No edit or read intent detected in user input.",
        )

    def _answer_from_tool_result(self, tool_result_content: list) -> FinalAnswerDecision:
        """
        Called on the second turn after a tool has been executed.
        Converts the raw tool result into a human-readable final answer.

        This mirrors what Claude does: it receives the tool result and
        writes a natural language response to the user.
        """
        for item in tool_result_content:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "tool_result":
                continue

            content  = item.get("content", "")
            is_error = item.get("is_error", False)

            if is_error:
                return FinalAnswerDecision(
                    content=f"The tool returned an error: {content}",
                    thinking="Tool call failed. Surfacing the error message.",
                )

            if content:
                return FinalAnswerDecision(
                    content=content,
                    thinking="Tool returned a result. Presenting it to the user.",
                )

            # Empty content = silent success (edit_document returns nothing)
            return FinalAnswerDecision(
                content="Operation completed successfully.",
                thinking="Tool returned empty content — likely a write/edit that succeeded silently.",
            )

        return FinalAnswerDecision(
            content="Done.",
            thinking="No recognisable tool result found in message.",
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _latest_user_text(messages: list) -> str:
        """Extract the text of the most recent user message."""
        for msg in reversed(messages):
            if msg["role"] != "user":
                continue
            content = msg["content"]
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        return block.get("text", "")
        return ""
