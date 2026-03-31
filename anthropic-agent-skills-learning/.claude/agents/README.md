# Agents — Reference Guide

## What is an Agent?

An **Agent** is a specialised sub-instance of Claude with its own identity,
instructions, and tool permissions. The main Claude session can **spawn** an
agent to handle a self-contained task, wait for its result, and continue.

Agents are isolated workers. They have no access to the main conversation
history, they run their task independently, and return a single result.

---

## Why Use Agents Instead of Doing the Work Inline?

| Situation | Use Agent? | Reason |
|---|---|---|
| Reading 20 files to explore a codebase | Yes | Keeps main context clean |
| Writing a feature | No | Main agent is better — needs full context |
| Running a security review of changed files | Yes | Isolated, read-only, focused role |
| Writing tests for an existing module | Yes | Specialised persona, no risk to source |
| Simple one-file edit | No | Overkill for a simple task |
| Parallel research tasks | Yes | Multiple agents can run independently |

**Core rule:** Use agents for **isolated, read-only, or highly specialised** tasks
where contaminating the main context would be wasteful or risky.

---

## How Agents Work — The Execution Model

```
Main Claude session
      │
      │ "I need a code review of these files"
      ▼
runSubagent("CodeReviewer", task_description)
      │
      ├──► CodeReviewer agent starts
      │         reads the files
      │         applies its own review instructions
      │         builds a structured report
      │         returns single message ◄──────┐
      │                                       │
      ▼                                       │
Main session receives the report ────────────┘
      │
      │ continues with the report in context
      ▼
```

Key facts:
- The main agent **waits** for the sub-agent to finish
- The sub-agent has **no memory** of previous sessions or conversations
- The sub-agent can only use the **tools listed in its definition**
- The sub-agent returns **one message only** — make sure the instructions ask for a complete output

---

## Agent Definition File — Anatomy

Each agent is defined by a Markdown file in `.claude/agents/`.

```
.claude/agents/
├── code-reviewer.md
└── test-writer.md
```

### Structure of an agent `.md` file

```markdown
---
name: AgentName            ← used in runSubagent("AgentName", ...)
description: >
  One paragraph description of what this agent does and when to use it.
  This is shown in the agents list and used to decide which agent to pick.
tools:                     ← list of tools this agent is allowed to use
  - read_file
  - grep_search
  - semantic_search
  - create_file            ← only include if the agent needs to write files
---

# Agent Title

[Full instructions for how this agent should behave]
[Be very specific — the agent has no other context]
```

---

## Agents in This Workspace

### `CodeReviewer`
**File:** `code-reviewer.md`
**Purpose:** Read-only code review producing a structured report with severity labels.

**Tools:** `read_file`, `grep_search`, `semantic_search`, `file_search`

**When to invoke:**
- After making changes — ask for a review before committing
- When you want a security, performance, or quality check
- When reviewing someone else's code

**Output format:**
```
## Code Review Report
### Summary
[overview]
### Findings
[BLOCKING] file:line — description
[SUGGESTION] file:line — description
[NITPICK] file:line — note
[PRAISE] file — something well done
### Recommendation: APPROVE | REQUEST CHANGES | ...
```

**Example invocation:**
> "Review the changes I made in src/auth.py"
> → Main agent spawns CodeReviewer with the file path

---

### `TestWriter`
**File:** `test-writer.md`
**Purpose:** Reads source files and generates comprehensive test files.

**Tools:** `read_file`, `grep_search`, `semantic_search`, `file_search`, `create_file`

**When to invoke:**
- When you have written a new function or module and need tests
- When test coverage is low and you want it improved
- When you want both happy path AND edge case tests generated

**Output:** Creates a test file at the correct location (e.g. `tests/test_module.py`)

**Example invocation:**
> "Write tests for src/utils/parser.py"
> → Main agent spawns TestWriter with the source file path

---

## How to Create a New Agent

### Step 1 — Create the file

```bash
touch .claude/agents/your-agent.md
```

### Step 2 — Write the definition

```markdown
---
name: YourAgentName
description: >
  What this agent does and the conditions under which the main agent
  should spawn it. Be specific so Claude can auto-select it.
tools:
  - read_file
  - grep_search
  - semantic_search
  # Add create_file only if the agent needs to write files
  # Add run_in_terminal only if the agent needs to run commands
---

# Your Agent Name

You are [persona description]. Your responsibility is [goal].

---

## Your Responsibilities

1. [First responsibility]
2. [Second responsibility]
3. Never modify source files (if read-only)

---

## Process

### Phase 1 — [First phase name]
[What the agent does first]

### Phase 2 — [Second phase name]
[What the agent does next]

### Phase 3 — Output
[Exact format of the agent's return message]

---

## Output Format

[Show the exact structure the agent should return]

## Rules

- [Rule 1]
- [Rule 2]
- [Rule 3]
```

### Step 3 — It's registered automatically

Agent files in `.claude/agents/` are picked up by VS Code / Claude Code
automatically. No additional configuration step needed.

---

## Tool Permissions — What to Give Each Agent Type

| Agent Role | Recommended Tools |
|---|---|
| Read-only explorer / reviewer | `read_file`, `grep_search`, `semantic_search`, `file_search` |
| Code generator / test writer | + `create_file` |
| Refactoring agent | + `replace_string_in_file` |
| Build / CI agent | + `run_in_terminal` |
| Full autonomous agent | All tools (use carefully) |

**Principle of least privilege:** Only give an agent the tools it actually needs.
A code reviewer should never have `run_in_terminal`.

---

## Writing Good Agent Instructions

| Principle | Detail |
|---|---|
| **State the persona clearly** | "You are a senior security engineer" sets tone and expertise |
| **Define scope explicitly** | "Never modify source files" prevents accidental writes |
| **Prescribe the output format** | The main agent needs to parse the result — be exact |
| **Break work into phases** | Phases (orient → analyse → report) give Claude a clear workflow |
| **No ambiguity** | Claude has no main conversation context — every instruction must be self-contained |

---

## Common Mistakes to Avoid

| Mistake | Problem | Fix |
|---|---|---|
| Vague description | Main Claude can't decide when to use the agent | Write specific triggering conditions |
| No output format defined | Main agent gets unstructured text, hard to use | Define exact output structure in the agent instructions |
| Too many tools | Agent can take unintended actions | Use minimum necessary tools |
| Assuming conversation context | Sub-agent doesn't have it | Make instructions fully self-contained |
| Returning multiple messages | Agents return ONE message | Consolidate everything into a single comprehensive output |

---

## Quick Reference

```
Location:      .claude/agents/<name>.md
Spawned by:    runSubagent("AgentName", task)
Context:       None — no access to main conversation history
Output:        Single message returned to main agent
Tools:         Only those listed in frontmatter
Best for:      Isolated, focused, read-only, or specialised tasks
Registration:  Automatic — files in .claude/agents/ are auto-discovered
```
