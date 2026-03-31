# 05 — Claude.md Files

## What Are Claude.md Files?

Claude.md files are persistent instruction files that Claude Code reads automatically on every request. They provide project context, coding conventions, and behavioral instructions without requiring manual repetition.

---

## File Locations and Hierarchy

```
~/.claude/Claude.md              ← Machine level (global)
./Claude.md                      ← Project level (committed to VCS)
./.claude/Claude.md              ← Local level (personal, not committed)
```

### Machine Level (`~/.claude/Claude.md`)

- Applied to **all** projects on your machine
- Personal preferences and global coding style
- Not shared with anyone

```markdown
## Global Preferences

- Always use type hints in Python
- Prefer f-strings over .format()
- Use early returns to reduce nesting
- Write commit messages in imperative mood
```

### Project Level (`./Claude.md`)

- Lives in the project root directory
- **Committed** to version control
- Shared with the entire team
- Should contain project-specific context

```markdown
## Project: E-Commerce API

### Stack
- Python 3.12, FastAPI, SQLAlchemy, PostgreSQL

### Architecture
- src/api/ — route handlers
- src/models/ — SQLAlchemy models
- src/services/ — business logic
- src/db/ — database migrations and schema

### Key Files
- src/db/schema.sql — database schema (reference before DB changes)
- src/api/deps.py — shared dependencies and auth

### Conventions
- All endpoints return Pydantic response models
- Use dependency injection for database sessions
- Tests mirror src/ structure in tests/
- Run `make lint && make test` before committing
```

### Local Level (`./.claude/Claude.md`)

- Personal instructions for a specific project
- **Not committed** to version control
- Overrides project-level where applicable

```markdown
## Personal Notes

- I prefer verbose logging when debugging
- Skip the "shall I proceed?" confirmations
- My test database is on port 5433
```

---

## Creating Claude.md with `/init`

The `/init` command analyzes your codebase and generates a project-level Claude.md:

```bash
# In Claude Code terminal
/init
```

Claude will:
1. Scan directory structure
2. Read key files (README, package.json, pyproject.toml, etc.)
3. Identify patterns and conventions
4. Generate a comprehensive Claude.md

---

## Editing with Memory Mode (`#`)

Use the `#` prefix to modify Claude.md via natural language:

```
# The main database model file is src/models/base.py
# Never modify the migrations/ directory directly — use alembic
# Prefer httpx over requests for async HTTP calls
```

Claude intelligently determines which Claude.md file to update and how to incorporate the instruction.

---

## Best Practices

### DO

- Reference critical files that Claude should always consider
- Include project architecture and directory layout
- Document naming conventions and coding standards
- List common commands (test, lint, build, deploy)
- Keep it concise — long files dilute important context

### DON'T

- Include entire file contents in Claude.md
- Add frequently changing information
- Duplicate what's already in README.md
- Add info that only applies to a single task (use conversation instead)

---

## Template

```markdown
# Project: [Name]

## Overview
[One-paragraph description]

## Stack
- [Language, frameworks, databases]

## Directory Structure
- `src/` — application source code
- `tests/` — test suite
- `docs/` — documentation

## Key Files
- `src/config.py` — application configuration
- `src/db/schema.sql` — database schema

## Conventions
- [Coding standards]
- [Naming patterns]
- [Testing requirements]

## Commands
- `make test` — run test suite
- `make lint` — run linters
- `make dev` — start development server
```

---

## Exercises

1. Create a machine-level Claude.md with your personal coding preferences
2. Write a project-level Claude.md for an existing project you're working on
3. Use memory mode (`#`) to add three important instructions
4. Compare the output quality of Claude Code with and without a Claude.md file
