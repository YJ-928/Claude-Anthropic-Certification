"""
exercise_08_tool_chaining.py
─────────────────────────────
Demonstrates:
  - Multi-step tool calling (Claude decides to call tools sequentially)
  - A realistic research assistant that chains:
      1. web_search (mocked)  →  2. summarize_text  →  3. translate_text
  - max_steps guard to prevent infinite loops
  - Logging each intermediate tool call

Run:
    python exercise_08_tool_chaining.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL

# ── Tool schemas ──────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for a topic and return a brief raw excerpt. "
            "Use this first to gather raw information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"],
        },
    },
    {
        "name": "summarize_text",
        "description": "Condense a long passage of text into 2–3 sentences.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to summarize."}
            },
            "required": ["text"],
        },
    },
    {
        "name": "translate_text",
        "description": "Translate a snippet of text into a target language.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text":            {"type": "string", "description": "Text to translate."},
                "target_language": {"type": "string", "description": "Target language, e.g. 'Spanish'."},
            },
            "required": ["text", "target_language"],
        },
    },
]

# ── Mock implementations (no real HTTP calls needed) ─────────────────────────

MOCK_SEARCH_DB = {
    "default": (
        "Photosynthesis is the process by which green plants and some other organisms "
        "use sunlight, water and carbon dioxide to produce oxygen and energy in the "
        "form of glucose. The process occurs in two stages: the light-dependent reactions "
        "and the Calvin cycle. Chlorophyll in the chloroplasts absorbs the light energy. "
        "Approximately 115 billion tonnes of carbon are fixed globally each year through photosynthesis."
    )
}


def web_search(query: str) -> str:
    key = query.lower().split()[0] if query else "default"
    return MOCK_SEARCH_DB.get(key, MOCK_SEARCH_DB["default"])


def summarize_text(text: str) -> str:
    """Use Claude itself to summarize (meta-tool)."""
    r = client.messages.create(
        model=FAST_MODEL,
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": f"Summarize this text in 2-3 sentences:\n\n{text}",
        }],
    )
    return r.content[0].text


def translate_text(text: str, target_language: str) -> str:
    """Use Claude itself to translate."""
    r = client.messages.create(
        model=FAST_MODEL,
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Translate the following text to {target_language}:\n\n{text}",
        }],
    )
    return r.content[0].text


# ── Dispatcher ────────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "web_search":
        return web_search(inputs["query"])
    if name == "summarize_text":
        return summarize_text(inputs["text"])
    if name == "translate_text":
        return translate_text(inputs["text"], inputs["target_language"])
    return f"Unknown tool: {name}"


# ── Chaining loop ─────────────────────────────────────────────────────────────

def run_chained_agent(user_message: str, max_steps: int = 8) -> str:
    messages = [{"role": "user", "content": user_message}]
    step = 0
    print(f"Task: {user_message}\n")

    while step < max_steps:
        step += 1
        response = client.messages.create(
            model=FAST_MODEL,
            max_tokens=512,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nFinal answer:\n{block.text}")
                    return block.text
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  Step {step} → [{block.name}] inputs: {block.input}")
                    result = run_tool(block.name, block.input)
                    print(f"            result: {result[:120]}{'...' if len(result)>120 else ''}")
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result,
                    })
            messages.append({"role": "user", "content": tool_results})

    return "Stopped: max_steps reached."


if __name__ == "__main__":
    print("=== Exercise 08 — Tool Chaining ===\n")
    run_chained_agent(
        "Search for information about photosynthesis, summarize it, "
        "then translate the summary into Spanish."
    )
