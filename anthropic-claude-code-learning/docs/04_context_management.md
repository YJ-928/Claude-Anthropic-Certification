# 04 — Context Management

## Why Context Matters

Context management is **critical** for Claude Code effectiveness. Providing too little context forces Claude to search and guess; too much irrelevant context decreases accuracy and wastes tokens.

> Goal: Provide just enough relevant information for Claude to complete tasks effectively.

---

## Context Sources

```
┌─────────────────────────────────────────────────────┐
│               Claude Code Context Stack              │
├─────────────────────────────────────────────────────┤
│  1. System prompt (built-in)                        │
│  2. Claude.md files (auto-loaded)                   │
│  3. @file mentions (user-specified)                 │
│  4. Conversation history                            │
│  5. Tool results (files read, commands run)         │
└─────────────────────────────────────────────────────┘
```

---

## The `/init` Command

When you first start working on a project, run `/init` to have Claude:

1. Analyze the entire codebase structure
2. Identify key files and patterns
3. Generate a `Claude.md` file summarizing the project
4. The file contents are included in **every subsequent request**

```bash
# In Claude Code terminal
/init
```

This creates a project-level `Claude.md` with:
- Project description and purpose
- Technology stack
- Directory structure overview
- Key files and their roles
- Coding conventions

---

## Claude.md File Hierarchy

Three levels of Claude.md files, each with a different scope:

```
┌───────────────────────────────────────────────┐
│  Machine Level (~/.claude/Claude.md)          │
│  → Global instructions for ALL projects       │
│  → Personal preferences, coding style         │
├───────────────────────────────────────────────┤
│  Project Level (./Claude.md)                  │
│  → Shared with team, committed to VCS         │
│  → Project architecture, conventions          │
├───────────────────────────────────────────────┤
│  Local Level (./.claude/Claude.md)            │
│  → Personal, NOT committed to VCS             │
│  → Individual workflow preferences            │
└───────────────────────────────────────────────┘
```

### Priority

Context is merged top-down. Local overrides project, which overrides machine.

---

## The `@` Symbol — File Mentions

Use `@` to include specific files in your request:

```
@src/models/user.py Add email validation to the User model
```

This provides targeted context instead of letting Claude search the entire codebase.

### When to Use `@`

- When you know exactly which file needs work
- When providing reference files (schemas, types, configs)
- When Claude's search might find the wrong file

---

## Memory Mode (`#`)

Use `#` to edit Claude.md files with natural language:

```
# Always use pytest for testing, never unittest
# The database schema is in src/db/schema.sql — always reference it
```

This intelligently updates the appropriate Claude.md file.

---

## Conversation Control Commands

### `Escape` — Stop and Redirect

Press Escape once to interrupt Claude's current output and redirect.

**Power move**: Stop Claude → add memory with `#` about repeated mistakes → prevent future errors.

### `Double Escape` — Conversation Rewind

Shows all previous messages. Jump back to an earlier point while maintaining relevant context and skipping irrelevant debugging loops.

### `/compact` — Summarize History

Summarizes entire conversation history while preserving Claude's learned knowledge about the current task. Use when the conversation has accumulated clutter but Claude has useful context.

### `/clear` — Fresh Start

Deletes all conversation history. Use when switching to a completely unrelated task.

---

## Context Best Practices

```python
# Example: Reference critical files in Claude.md

# Claude.md content:
"""
## Key Files
- Database schema: src/db/schema.sql (always reference before DB changes)
- API routes: src/api/routes.py
- Config: src/config.py

## Conventions
- Use type hints on all function signatures
- Tests go in tests/ mirroring src/ structure
- Run `make lint` before committing
"""
```

---

## Architecture Diagram — Context Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Machine       │     │ Project      │     │ Local        │
│ Claude.md     │     │ Claude.md    │     │ Claude.md    │
│ (global)      │     │ (team)       │     │ (personal)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ↓
                   ┌────────────────┐
                   │ Merged Context │
                   └────────┬───────┘
                            ↓
              ┌─────────────────────────┐
              │ + @file mentions        │
              │ + conversation history  │
              │ + tool results          │
              └─────────────┬───────────┘
                            ↓
                   ┌────────────────┐
                   │  Claude API    │
                   └────────────────┘
```

---

## Exercises

1. Create a Claude.md file for a Python web application project
2. Practice using `/compact` and `/clear` — note when each is appropriate
3. Write three memory entries using `#` that would prevent common mistakes in your project
4. Explain the difference between project-level and local-level Claude.md files
