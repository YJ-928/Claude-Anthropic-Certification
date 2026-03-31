"""
exercise_10_prompt_eval.py
───────────────────────────
Demonstrates:
  - Building a small evaluation (eval) dataset
  - Code-based grading (exact match / substring match)
  - Model-based grading (Claude-as-judge via Haiku)
  - Printing a summary scorecard

Run:
    python exercise_10_prompt_eval.py
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL

# ── Eval dataset ──────────────────────────────────────────────────────────────
# Each item: {"input": <user message>, "expected": <ideal answer>,
#             "grader": "exact" | "contains" | "model"}

EVAL_DATASET = [
    {
        "input":    "What is 2 + 2?",
        "expected": "4",
        "grader":   "contains",
    },
    {
        "input":    "What is the capital of France?",
        "expected": "Paris",
        "grader":   "contains",
    },
    {
        "input":    "In one word, what color is the sky?",
        "expected": "blue",
        "grader":   "exact",
    },
    {
        "input":    "Explain why the sky is blue in one sentence.",
        "expected": (
            "The sky appears blue because of Rayleigh scattering, "
            "where shorter blue wavelengths scatter more than other colors."
        ),
        "grader":   "model",
    },
    {
        "input":    "Write a haiku about rain.",
        "expected": "A valid haiku with 5-7-5 syllable structure about rain.",
        "grader":   "model",
    },
]

# ── System prompt being tested ────────────────────────────────────────────────

SYSTEM_PROMPT = "You are a concise assistant. Answer in as few words as possible."


# ── Graders ───────────────────────────────────────────────────────────────────

def grade_exact(actual: str, expected: str) -> tuple[bool, str]:
    passed = actual.strip().lower() == expected.strip().lower()
    return passed, "exact match" if passed else "mismatch"


def grade_contains(actual: str, expected: str) -> tuple[bool, str]:
    passed = expected.strip().lower() in actual.strip().lower()
    return passed, "found expected" if passed else "expected not found"


GRADER_SYSTEM = """
You are an impartial grader. You will be given an expected answer and an actual answer.
Reply with a JSON object:
{
  "pass": true | false,
  "reason": "<one sentence explanation>"
}
Only return the JSON object, no other text.
"""


def grade_model(actual: str, expected: str) -> tuple[bool, str]:
    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=128,
        temperature=0.0,
        system=GRADER_SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                f"Expected: {expected}\n\nActual: {actual}\n\n"
                f"Does the actual answer satisfy the expected criterion?"
            ),
        }],
    )
    raw = response.content[0].text.strip()
    try:
        result = json.loads(raw)
        return bool(result.get("pass", False)), result.get("reason", "")
    except json.JSONDecodeError:
        # Fallback: check for 'true' in raw text
        passed = '"pass": true' in raw.lower()
        return passed, raw[:80]


# ── Get model answer ──────────────────────────────────────────────────────────

def get_answer(user_message: str) -> str:
    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()


# ── Run eval ──────────────────────────────────────────────────────────────────

def run_eval(dataset: list[dict]) -> None:
    results = []
    print(f"{'#':<3}  {'Input':<45}  {'Grader':<8}  {'Pass':<5}  Reason")
    print("-" * 100)

    for idx, item in enumerate(dataset, 1):
        actual = get_answer(item["input"])
        grader_type = item["grader"]

        if grader_type == "exact":
            passed, reason = grade_exact(actual, item["expected"])
        elif grader_type == "contains":
            passed, reason = grade_contains(actual, item["expected"])
        else:
            passed, reason = grade_model(actual, item["expected"])

        results.append(passed)
        status = "✓" if passed else "✗"
        short_input = item["input"][:43]
        print(f"{idx:<3}  {short_input:<45}  {grader_type:<8}  {status:<5}  {reason}")
        print(f"       Actual: {actual[:90]}")
        print()

    total  = len(results)
    passed = sum(results)
    print(f"\nScore: {passed}/{total} = {passed/total*100:.1f}%")


if __name__ == "__main__":
    print("=== Exercise 10 — Prompt Evaluation ===\n")
    print(f"System prompt: {SYSTEM_PROMPT!r}\n")
    run_eval(EVAL_DATASET)
