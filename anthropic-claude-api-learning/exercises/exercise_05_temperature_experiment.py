"""
exercise_05_temperature_experiment.py
──────────────────────────────────────
Demonstrates:
  - How temperature (0.0 → 1.0) affects creativity and consistency
  - Sampling the same prompt multiple times to see variance
  - Practical guidance: what temperature values to use and when

Run:
    python exercise_05_temperature_experiment.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL


TEMPERATURES = [0.0, 0.5, 1.0]
SAMPLES_PER_TEMP = 3

CREATIVE_PROMPT = "Give me a one-sentence tagline for a coffee shop called 'The Sleepy Mug'."
FACTUAL_PROMPT  = "What is the boiling point of water at sea level in Celsius?"


def sample_prompt(prompt: str, temperature: float, n: int = 3) -> list[str]:
    """Call Claude n times at a given temperature and return the replies."""
    results = []
    for i in range(n):
        response = client.messages.create(
            model=FAST_MODEL,
            max_tokens=80,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        results.append(response.content[0].text.strip())
    return results


def run_experiment(prompt: str, label: str) -> None:
    print(f"\n{'='*60}")
    print(f"  Prompt type: {label}")
    print(f"  Prompt: {prompt!r}")
    print(f"{'='*60}")

    for temp in TEMPERATURES:
        print(f"\n  Temperature = {temp}  ({SAMPLES_PER_TEMP} samples)")
        replies = sample_prompt(prompt, temperature=temp, n=SAMPLES_PER_TEMP)
        for idx, reply in enumerate(replies, 1):
            print(f"    [{idx}] {reply}")


if __name__ == "__main__":
    print("=== Exercise 05 — Temperature Experiment ===")
    print(f"Running {SAMPLES_PER_TEMP} samples at temperatures {TEMPERATURES}")
    print("(This makes multiple API calls — may take a minute)\n")

    run_experiment(CREATIVE_PROMPT, "Creative / Open-ended")
    run_experiment(FACTUAL_PROMPT,  "Factual / Deterministic")

    print("\n\nKey observations:")
    print("  temperature=0.0 → near-deterministic; ideal for facts, code, JSON")
    print("  temperature=0.5 → balanced; good for chat, Q&A, summaries")
    print("  temperature=1.0 → high variance; great for brainstorming, creative writing")
