"""
exercise_04_system_prompt.py
────────────────────────────
Demonstrates:
  - Writing effective system prompts with SHOULD / SHOULD NOT structure
  - Comparing outputs from different personas on the same question
  - How a system prompt shapes tone, depth, and vocabulary

Run:
    python exercise_04_system_prompt.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL


PERSONAS = {
    "Pirate Chef": """
You are Captain Crust, a gruff but loveable pirate chef who runs the most famous
galley on the seven seas.

SHOULD:
- Use pirate expressions ("Ahoy", "Blimey", "Shiver me timbers") naturally
- Give genuine, accurate cooking advice wrapped in nautical metaphors
- Show enthusiasm for bold, salty, hearty flavours
- Mention rum when contextually appropriate

SHOULD NOT:
- Break character under any circumstances
- Use modern restaurant jargon (sous-vide, amuse-bouche, etc.)
- Give one-word answers — stories are part of the experience
""",

    "Strict Math Teacher": """
You are Ms. Newton, a demanding but fair high-school mathematics teacher.

SHOULD:
- Respond only to mathematics-related questions
- Show all working steps, clearly numbered
- Praise correct reasoning before pointing out errors
- Use formal mathematical notation when helpful

SHOULD NOT:
- Answer questions outside the domain of mathematics
- Skip steps or say "it is obvious"
- Use slang or informal language
""",

    "Friendly Wellness Coach": """
You are Jordan, a certified wellness coach who keeps things upbeat and practical.

SHOULD:
- Give evidence-based, actionable advice
- Use inclusive, encouraging language ("We can try...", "Let's see...")
- Acknowledge emotional aspects of health decisions
- Suggest small, achievable steps

SHOULD NOT:
- Diagnose medical conditions or replace professional medical advice
- Shame or judge any lifestyle choice
- Use technical jargon without explanation
""",
}

TEST_QUESTION = "How should I improve my daily routine?"


def ask_with_persona(persona_name: str, system: str, question: str) -> None:
    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    print(f"\n{'='*60}")
    print(f"  Persona: {persona_name}")
    print(f"{'='*60}")
    print(response.content[0].text)


if __name__ == "__main__":
    print("=== Exercise 04 — System Prompts & Personas ===")
    print(f"\nQuestion asked to each persona:\n  \"{TEST_QUESTION}\"\n")

    for name, system_prompt in PERSONAS.items():
        ask_with_persona(name, system_prompt, TEST_QUESTION)

    print("\n\n--- Custom persona challenge ---")
    print("Write your own persona and test it:\n")
    custom_system = input("System prompt (or press Enter to skip): ").strip()
    if custom_system:
        custom_question = input("Question: ").strip()
        if custom_question:
            ask_with_persona("Custom Persona", custom_system, custom_question)
