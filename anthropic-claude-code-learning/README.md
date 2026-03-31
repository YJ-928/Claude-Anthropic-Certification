# Anthropic Claude Code Learning

A comprehensive learning repository for the **Claude Code in Action** course from Anthropic Academy.

This repository covers Claude Code architecture, tool use, context management, hooks, custom commands, the Claude Code SDK, GitHub Actions integration, and MCP server extensions.

---

## Repository Structure

```
anthropic-claude-code-learning/
├── README.md
├── requirements.txt
├── .env.example
├── docs/                        # 15 detailed concept documents
│   ├── 01_coding_assistants.md
│   ├── 02_claude_code_architecture.md
│   ├── 03_tool_use_for_coding.md
│   ├── ...
│   └── 15_best_practices.md
├── notebooks/                   # 5 interactive Jupyter notebooks
│   ├── 01_coding_assistant_architecture.ipynb
│   ├── ...
│   └── 05_sdk_usage.ipynb
├── exercises/                   # 7 standalone exercises
│   ├── exercise_01_tool_read_file.py
│   ├── ...
│   └── exercise_07_sdk_query.py
├── projects/
│   ├── claude_code_cli/         # Simplified coding assistant CLI
│   ├── hooks_demo/              # Hook preventing .env access
│   ├── custom_commands/         # Example custom commands
│   └── sdk_demo/                # Claude Code SDK examples
└── utils/                       # Shared utilities
    ├── tool_parser.py
    ├── context_utils.py
    └── git_helpers.py
```

---

## Prerequisites

- Python 3.11+
- Node.js (for hook demos)
- An Anthropic API key

---

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd anthropic-claude-code-learning

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

---

## Learning Path

### Phase 1 — Foundations
| # | Topic | Doc | Notebook |
|---|-------|-----|----------|
| 1 | Coding Assistants | [01_coding_assistants.md](docs/01_coding_assistants.md) | [01_coding_assistant_architecture.ipynb](notebooks/01_coding_assistant_architecture.ipynb) |
| 2 | Claude Code Architecture | [02_claude_code_architecture.md](docs/02_claude_code_architecture.md) | — |
| 3 | Tool Use for Coding | [03_tool_use_for_coding.md](docs/03_tool_use_for_coding.md) | [03_tool_use.ipynb](notebooks/03_tool_use.ipynb) |
| 4 | Context Management | [04_context_management.md](docs/04_context_management.md) | [02_context_management.ipynb](notebooks/02_context_management.ipynb) |
| 5 | Claude.md Files | [05_claude_md_files.md](docs/05_claude_md_files.md) | — |

### Phase 2 — Workflow
| # | Topic | Doc | Exercise |
|---|-------|-----|----------|
| 6 | Planning & Thinking Modes | [06_planning_and_thinking_modes.md](docs/06_planning_and_thinking_modes.md) | — |
| 7 | Git Integration | [07_git_integration.md](docs/07_git_integration.md) | — |
| 8 | Custom Commands | [08_custom_commands.md](docs/08_custom_commands.md) | [exercise_04](exercises/exercise_04_custom_command.py) |

### Phase 3 — Hooks
| # | Topic | Doc | Exercise |
|---|-------|-----|----------|
| 9 | Hooks Introduction | [09_hooks_intro.md](docs/09_hooks_intro.md) | [exercise_05](exercises/exercise_05_pre_tool_hook.py) |
| 10 | Pre/Post Tool Hooks | [10_hooks_pre_post_tools.md](docs/10_hooks_pre_post_tools.md) | [exercise_06](exercises/exercise_06_post_tool_hook.py) |
| 11 | Hook Implementation | [11_hook_implementation.md](docs/11_hook_implementation.md) | — |

### Phase 4 — SDK & Extensions
| # | Topic | Doc | Exercise |
|---|-------|-----|----------|
| 12 | Claude Code SDK | [12_claude_code_sdk.md](docs/12_claude_code_sdk.md) | [exercise_07](exercises/exercise_07_sdk_query.py) |
| 13 | GitHub Actions Integration | [13_github_actions_integration.md](docs/13_github_actions_integration.md) | — |
| 14 | MCP Server Extensions | [14_mcp_server_extensions.md](docs/14_mcp_server_extensions.md) | — |
| 15 | Best Practices | [15_best_practices.md](docs/15_best_practices.md) | — |

---

## Projects

| Project | Description | Directory |
|---------|-------------|-----------|
| Claude Code CLI | Simplified coding assistant with tool execution | [projects/claude_code_cli](projects/claude_code_cli/) |
| Hooks Demo | Pre-tool hook blocking `.env` file access | [projects/hooks_demo](projects/hooks_demo/) |
| Custom Commands | Example `/audit` and `/generate-tests` commands | [projects/custom_commands](projects/custom_commands/) |
| SDK Demo | Programmatic Claude Code queries and pipelines | [projects/sdk_demo](projects/sdk_demo/) |

---

## Key Concepts

### Tool Use Loop

```
User Request
     ↓
Language Model (Claude)
     ↓
Tool Call Decision (read_file, write_file, run_command, search_code)
     ↓
Tool Executor (application layer)
     ↓
Result fed back to Claude
     ↓
Final Response to User
```

### Hook System

```
Tool Call Initiated
     ↓
Pre-tool-use Hook → exit 0 (allow) or exit 2 (block)
     ↓
Tool Executes (if allowed)
     ↓
Post-tool-use Hook → feedback / follow-up actions
```

---

## License

This repository is for educational purposes as part of the Anthropic Academy curriculum.
