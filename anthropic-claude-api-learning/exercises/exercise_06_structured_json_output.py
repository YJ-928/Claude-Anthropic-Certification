"""
exercise_06_structured_json_output.py
──────────────────────────────────────
Demonstrates three techniques to get reliable JSON from Claude:
  1. Pre-filling the assistant turn with '{'
  2. Adding a stop sequence to close after the JSON object
  3. Forcing tool_choice="any" so the model always calls a tool

Run:
    python exercise_06_structured_json_output.py
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL


# ── Technique 1: Pre-fill + stop sequence ─────────────────────────────────────

def extract_via_prefill(text: str) -> dict:
    """
    Ask Claude to extract entities and start its reply with '{',
    then stop at '}' to ensure we capture exactly one JSON object.
    """
    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=256,
        stop_sequences=["}"],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Extract the person's name, age, and city from this text "
                    f"as a JSON object with keys 'name', 'age', 'city'.\n\nText: {text}"
                ),
            },
            # Pre-fill: force the assistant to begin with JSON
            {"role": "assistant", "content": "{"},
        ],
    )
    # Reconstruct: prepend the '{' we pre-filled, append the '}' stop consumed
    raw = "{" + response.content[0].text + "}"
    return json.loads(raw)


# ── Technique 2: Forced tool_choice ──────────────────────────────────────────

EXTRACT_TOOL = {
    "name": "extract_person",
    "description": "Extract structured person data from unstructured text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string",  "description": "Full name of the person"},
            "age":  {"type": "integer", "description": "Age in years"},
            "city": {"type": "string",  "description": "City of residence"},
        },
        "required": ["name", "age", "city"],
    },
}


def extract_via_tool(text: str) -> dict:
    """Force the model to return structured data via tool_choice='any'."""
    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=256,
        tools=[EXTRACT_TOOL],
        tool_choice={"type": "any"},   # guarantees a tool call
        messages=[
            {
                "role": "user",
                "content": f"Extract person info from:\n\n{text}",
            }
        ],
    )
    # Find the tool_use block in the response
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise ValueError("No tool_use block found — did tool_choice not work?")


# ── Test it out ───────────────────────────────────────────────────────────────

SAMPLE_TEXTS = [
    "Meet Sarah Johnson, a 34-year-old software engineer who lives in Austin.",
    "The patient, Mr. Carlos Ruiz (age 52) is originally from Madrid.",
]

if __name__ == "__main__":
    print("=== Exercise 06 — Structured JSON Output ===\n")

    for text in SAMPLE_TEXTS:
        print(f"Input: {text!r}\n")

        result1 = extract_via_prefill(text)
        print(f"  Technique 1 (pre-fill):  {result1}")

        result2 = extract_via_tool(text)
        print(f"  Technique 2 (tool):      {result2}")
        print()
