"""
main.py — Interactive CLI entry point for the Reminder Agent.

Run:
    python -m projects.tool_agent_reminder.main
  or from the project directory:
    python main.py

Commands:
  Type any reminder request in natural language.
  list     → show all reminders
  clear    → reset conversation history
  quit     → exit
"""
from .agent import ReminderAgent


def main() -> None:
    print("=== Claude Reminder Agent ===")
    print("Commands: 'list', 'clear', 'quit'\n")
    print("Examples:")
    print("  Remind me to take a break in 30 minutes.")
    print("  Set a reminder for the team meeting tomorrow at 9am.")
    print()

    agent = ReminderAgent(verbose=True)

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if user_input.lower() == "list":
            print(agent.get_reminders())
            continue

        if user_input.lower() == "clear":
            agent.reset()
            print("Conversation history cleared.\n")
            continue

        print()  # blank line before tool output
        reply = agent.chat(user_input)
        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    main()
