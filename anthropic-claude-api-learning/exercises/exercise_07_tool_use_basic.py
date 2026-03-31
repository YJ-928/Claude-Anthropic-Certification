"""
exercise_07_tool_use_basic.py
──────────────────────────────
Demonstrates:
  - Defining a tool with a JSON schema
  - Handling a tool_use response from Claude
  - Running the real Python function and feeding results back
  - The full tool-use conversation loop (user → model → tool → model)

Run:
    python exercise_07_tool_use_basic.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "calculate",
        "description": (
            "Perform a mathematical calculation. Supports: +, -, *, /, ** (power), "
            "sqrt(x), log(x), sin(x), cos(x). "
            "Returns the numeric result as a float."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A valid Python mathematical expression, e.g. '2 ** 8' or 'sqrt(144)'.",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_word_count",
        "description": "Count the number of words in a given text string.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to count words in."}
            },
            "required": ["text"],
        },
    },
]


# ── Tool implementations ──────────────────────────────────────────────────────

def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    # Only allow a restricted namespace to prevent code injection
    safe_names = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    safe_names.update({"abs": abs, "round": round})
    try:
        result = eval(expression, {"__builtins__": {}}, safe_names)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def get_word_count(text: str) -> str:
    return str(len(text.split()))


# ── Dispatcher ────────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "calculate":
        return calculate(inputs["expression"])
    if name == "get_word_count":
        return get_word_count(inputs["text"])
    return f"Unknown tool: {name}"


# ── Agentic conversation loop ─────────────────────────────────────────────────

def agent_loop(user_message: str, max_steps: int = 5) -> str:
    messages = [{"role": "user", "content": user_message}]
    print(f"User: {user_message}\n")

    for step in range(max_steps):
        response = client.messages.create(
            model=FAST_MODEL,
            max_tokens=512,
            tools=TOOLS,
            messages=messages,
        )

        # Add assistant turn to history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Final text answer
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"Claude: {block.text}")
                    return block.text
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    print(f"  [Tool] {block.name}({block.input}) → {result}")
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result,
                    })
            messages.append({"role": "user", "content": tool_results})

    return "Max steps reached."


if __name__ == "__main__":
    print("=== Exercise 07 — Tool Use (Basic) ===\n")

    queries = [
        "What is the square root of 1764?",
        "How many words are in the sentence: 'The quick brown fox jumps over the lazy dog'?",
        "Calculate (3 ** 4) + log(100) and tell me the result.",
    ]

    for q in queries:
        print("-" * 50)
        agent_loop(q)
        print()
