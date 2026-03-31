# Anthropic MCP Learning

A comprehensive learning repository for the **Model Context Protocol (MCP)** — Anthropic's open standard for connecting AI models to external tools and data sources.

Based on the [Introduction to Model Context Protocol](https://github.com/anthropics/courses) course from Anthropic Academy.

---

## What is MCP?

The **Model Context Protocol** is a communication layer that provides Claude with context and tools without requiring developers to write tedious boilerplate code. MCP shifts tool definition and execution from your application server to dedicated MCP servers, dramatically reducing the developer burden of integrating external services.

### Key Benefits

- **Eliminates manual tool schema authoring** — MCP servers auto-generate JSON schemas from decorated Python functions
- **Reusable integrations** — Service providers create official MCP servers once, everyone benefits
- **Standardized protocol** — One client interface works with any MCP server
- **Three primitives** — Tools (model-controlled), Resources (app-controlled), Prompts (user-controlled)

---

## Repository Structure

```
anthropic-mcp-learning/
├── README.md
├── requirements.txt
├── .env.example
│
├── docs/                          # Concept documentation
│   ├── 01_mcp_overview.md
│   ├── 02_mcp_architecture.md
│   ├── 03_mcp_clients.md
│   ├── 04_mcp_servers.md
│   ├── 05_tools.md
│   ├── 06_resources.md
│   ├── 07_prompts.md
│   ├── 08_server_inspector.md
│   ├── 09_mcp_client_implementation.md
│   ├── 10_mcp_server_implementation.md
│   ├── 11_mcp_cli_chatbot_project.md
│   └── 12_mcp_best_practices.md
│
├── notebooks/                     # Interactive Jupyter notebooks
│   ├── 01_mcp_intro.ipynb
│   ├── 02_tools.ipynb
│   ├── 03_resources.ipynb
│   ├── 04_prompts.ipynb
│   ├── 05_mcp_client_server.ipynb
│   └── 06_cli_chatbot.ipynb
│
├── exercises/                     # Standalone exercise scripts
│   ├── exercise_01_simple_tool.py
│   ├── exercise_02_document_reader_tool.py
│   ├── exercise_03_document_edit_tool.py
│   ├── exercise_04_resource_endpoint.py
│   ├── exercise_05_prompt_template.py
│   └── exercise_06_client_tool_call.py
│
├── projects/
│   ├── mcp_document_server/       # Full MCP server implementation
│   │   ├── server.py
│   │   ├── tools.py
│   │   ├── resources.py
│   │   ├── prompts.py
│   │   └── documents.py
│   │
│   ├── mcp_document_client/       # Full MCP client implementation
│   │   ├── client.py
│   │   ├── chat_interface.py
│   │   └── conversation.py
│   │
│   └── cli_chatbot/               # End-to-end CLI chatbot
│       ├── main.py
│       ├── config.py
│       └── conversation_runner.py
│
└── utils/
    ├── anthropic_client.py
    └── mcp_helpers.py
```

---

## Quick Start

### 1. Clone and install

```bash
cd anthropic-mcp-learning
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 3. Test the MCP server with the Inspector

```bash
mcp dev projects/mcp_document_server/server.py
```

Open the localhost URL printed in the terminal to test tools, resources, and prompts interactively.

### 4. Run the CLI chatbot

```bash
python projects/cli_chatbot/main.py
```

---

## Learning Path

| Step | Topic | Resources |
|------|-------|-----------|
| 1 | MCP Overview | [docs/01](docs/01_mcp_overview.md), [notebook 01](notebooks/01_mcp_intro.ipynb) |
| 2 | Architecture | [docs/02](docs/02_mcp_architecture.md) |
| 3 | Clients | [docs/03](docs/03_mcp_clients.md) |
| 4 | Servers | [docs/04](docs/04_mcp_servers.md) |
| 5 | Tools | [docs/05](docs/05_tools.md), [notebook 02](notebooks/02_tools.ipynb), [exercise 01-03](exercises/) |
| 6 | Resources | [docs/06](docs/06_resources.md), [notebook 03](notebooks/03_resources.ipynb), [exercise 04](exercises/) |
| 7 | Prompts | [docs/07](docs/07_prompts.md), [notebook 04](notebooks/04_prompts.ipynb), [exercise 05](exercises/) |
| 8 | Server Inspector | [docs/08](docs/08_server_inspector.md) |
| 9 | Client Implementation | [docs/09](docs/09_mcp_client_implementation.md), [notebook 05](notebooks/05_mcp_client_server.ipynb), [exercise 06](exercises/) |
| 10 | Server Implementation | [docs/10](docs/10_mcp_server_implementation.md) |
| 11 | CLI Chatbot Project | [docs/11](docs/11_mcp_cli_chatbot_project.md), [notebook 06](notebooks/06_cli_chatbot.ipynb) |
| 12 | Best Practices | [docs/12](docs/12_mcp_best_practices.md) |

---

## Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)
- Basic familiarity with async Python and the Anthropic API

---

## License

Educational use only. Based on Anthropic Academy course materials.
