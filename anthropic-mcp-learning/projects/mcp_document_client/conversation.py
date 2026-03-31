"""
Conversation Manager

Extends the base chat interface with document-aware features:
- @document_name mentions for auto-including document content
- /command support for server-defined prompts
"""

from typing import Tuple

from mcp.types import Prompt, PromptMessage
from anthropic import Anthropic

from .client import MCPClient
from .chat_interface import ChatInterface


class Conversation(ChatInterface):
    """Document-aware conversation manager with resource and prompt support."""

    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        anthropic_client: Anthropic,
        model: str,
    ):
        super().__init__(
            anthropic_client=anthropic_client,
            model=model,
            clients=clients,
        )
        self.doc_client = doc_client

    # ─── Resource access ───────────────────────────────────

    async def list_doc_ids(self) -> list[str]:
        """Get list of available document IDs from the server."""
        return await self.doc_client.read_resource("docs://documents")

    async def get_doc_content(self, doc_id: str) -> str:
        """Get the content of a specific document."""
        return await self.doc_client.read_resource(f"docs://documents/{doc_id}")

    # ─── Prompt access ─────────────────────────────────────

    async def list_prompts(self) -> list[Prompt]:
        """Get available prompt templates from the server."""
        return await self.doc_client.list_prompts()

    async def get_prompt(
        self, command: str, doc_id: str
    ) -> list[PromptMessage]:
        """Fetch a prompt by name with the given document ID."""
        return await self.doc_client.get_prompt(command, {"doc_id": doc_id})

    # ─── @ mentions ────────────────────────────────────────

    async def _extract_resources(self, query: str) -> str:
        """Extract @mentioned documents and include their content."""
        mentions = [word[1:] for word in query.split() if word.startswith("@")]
        doc_ids = await self.list_doc_ids()
        mentioned_docs: list[Tuple[str, str]] = []

        for doc_id in doc_ids:
            if doc_id in mentions:
                content = await self.get_doc_content(doc_id)
                mentioned_docs.append((doc_id, content))

        return "".join(
            f'\n<document id="{doc_id}">\n{content}\n</document>\n'
            for doc_id, content in mentioned_docs
        )

    # ─── / commands ────────────────────────────────────────

    async def _process_command(self, query: str) -> bool:
        """Check if query is a slash command and process it."""
        if not query.startswith("/"):
            return False

        words = query.split()
        command = words[0].replace("/", "")

        if len(words) < 2:
            print(f"  Usage: /{command} <doc_id>")
            return False

        doc_id = words[1]

        try:
            messages = await self.doc_client.get_prompt(
                command, {"doc_id": doc_id}
            )
            # Convert PromptMessages to Anthropic message format
            for msg in messages:
                content = msg.content
                if hasattr(content, "text"):
                    text = content.text
                elif isinstance(content, str):
                    text = content
                else:
                    text = str(content)
                role = "user" if msg.role == "user" else "assistant"
                self.messages.append({"role": role, "content": text})
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    # ─── Override run to support commands and mentions ──────

    async def run(self, user_message: str) -> str:
        """Run a conversation turn with support for / commands and @ mentions."""
        # Handle slash commands
        if user_message.startswith("/"):
            if await self._process_command(user_message):
                # Run the prompt through Claude after adding to messages
                tools = await self.get_all_tools()
                while True:
                    response = self.anthropic.messages.create(
                        model=self.model,
                        max_tokens=8000,
                        messages=self.messages,
                        tools=tools,
                    )
                    self.messages.append(
                        {"role": "assistant", "content": response.content}
                    )
                    if response.stop_reason == "tool_use":
                        text = self._extract_text(response)
                        if text.strip():
                            print(f"  {text}")
                        tool_results = await self._execute_tool_requests(response)
                        self.messages.append({"role": "user", "content": tool_results})
                    else:
                        return self._extract_text(response)
            return "Command not recognized. Available commands: /format, /summarize"

        # Handle @ mentions — inject document context into the prompt
        added_resources = await self._extract_resources(user_message)

        prompt = f"""
        The user has a question:
        <query>
        {user_message}
        </query>

        The following context may be useful:
        <context>
        {added_resources}
        </context>

        Note: "@document_name" references mean the user mentioned a document.
        If the document content is included above, use it directly without calling a tool.
        Answer the user's question directly and concisely.
        """

        return await super().run(prompt)
