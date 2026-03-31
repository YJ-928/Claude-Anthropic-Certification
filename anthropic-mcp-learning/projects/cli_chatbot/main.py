"""
CLI Chatbot — Main Entry Point

An interactive command-line chatbot that connects to MCP servers
and uses Claude to answer questions with tool support.

Usage:
    python -m projects.cli_chatbot.main
    python projects/cli_chatbot/main.py
"""

import sys
import os
import asyncio
from contextlib import AsyncExitStack

# Allow direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
from anthropic import Anthropic

from projects.mcp_document_client.client import MCPClient
from projects.mcp_document_client.conversation import Conversation
from projects.cli_chatbot.config import Config


BANNER = """
╔══════════════════════════════════════════════════╗
║      MCP Document Chatbot — Powered by Claude    ║
╚══════════════════════════════════════════════════╝

Commands:
  @doc_id    — Mention a document to include its content
  /format    — Format a document (e.g. /format report.pdf)
  /summarize — Summarize a document (e.g. /summarize plan.md)
  /docs      — List available documents
  /help      — Show this help message
  /quit      — Exit the chatbot
"""


async def run_chatbot():
    """Main chatbot loop."""
    load_dotenv()
    config = Config.from_env()

    anthropic_client = Anthropic(api_key=config.api_key)

    # Path to the document server
    server_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "mcp_document_server",
        "server.py",
    )

    exit_stack = AsyncExitStack()
    try:
        # Connect to the MCP document server
        doc_client = MCPClient(command="python", args=[server_path])
        await exit_stack.enter_async_context(doc_client)

        # Create the conversation manager
        conversation = Conversation(
            doc_client=doc_client,
            clients={"documents": doc_client},
            anthropic_client=anthropic_client,
            model=config.model,
        )

        print(BANNER)

        # Print available documents
        doc_ids = await doc_client.read_resource("docs://documents")
        print(f"  Available documents: {', '.join(doc_ids)}")
        print()

        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            # Handle built-in commands
            if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
                print("Goodbye!")
                break

            if user_input.lower() == "/help":
                print(BANNER)
                continue

            if user_input.lower() == "/docs":
                doc_ids = await doc_client.read_resource("docs://documents")
                print(f"  Available documents: {', '.join(doc_ids)}")
                continue

            # Run conversation
            try:
                response = await conversation.run(user_input)
                print(f"\nClaude: {response}\n")
            except Exception as e:
                print(f"\n  Error: {e}\n")

    finally:
        await exit_stack.aclose()


def main():
    """Entry point."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(run_chatbot())


if __name__ == "__main__":
    main()
