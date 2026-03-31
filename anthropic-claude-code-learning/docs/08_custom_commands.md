# 08 — Custom Commands

## What Are Custom Commands?

Custom commands are user-defined automation commands in Claude Code, accessed via the forward slash (`/`) prefix. They allow you to package complex or repetitive instructions into reusable shortcuts.

---

## Directory Structure

```
project/
└── .claude/
    └── commands/
        ├── audit.md          → /audit
        ├── test_generator.md → /test_generator
        └── review.md         → /review
```

- **Location**: `.claude/commands/` folder in your project directory
- **Naming**: The filename (without `.md`) becomes the command name
- **Format**: Markdown files containing instructions for Claude

---

## Creating a Command

### Step 1: Create the directory

```bash
mkdir -p .claude/commands
```

### Step 2: Write the command file

**`.claude/commands/audit.md`** — Dependency audit command:

```markdown
Review all dependencies in this project for:

1. Known security vulnerabilities
2. Outdated versions with available updates
3. Unused dependencies that can be removed
4. License compatibility issues

For each issue found, provide:
- Severity (critical/high/medium/low)
- Current version vs recommended version
- Remediation steps

Output a summary table at the end.
```

### Step 3: Restart Claude Code

Commands are loaded at startup. Restart Claude Code after creating or modifying command files.

### Step 4: Use the command

```
/audit
```

---

## Using Arguments

Commands can accept runtime arguments using the `$ARGUMENTS` placeholder:

**`.claude/commands/test_generator.md`**:

```markdown
Generate comprehensive tests for the file: $ARGUMENTS

Include:
1. Unit tests for all public functions
2. Edge cases (empty input, null values, boundary conditions)
3. Error handling tests
4. Use pytest with descriptive test names
5. Add docstrings explaining what each test verifies

Follow the existing test patterns in the tests/ directory.
```

Usage:

```
/test_generator src/models/user.py
```

The `$ARGUMENTS` placeholder is replaced with `src/models/user.py`.

---

## Example Commands

### `/review` — Code Review

```markdown
Perform a thorough code review of $ARGUMENTS:

1. **Correctness**: Logic errors, off-by-one, null handling
2. **Security**: Input validation, injection risks, auth checks
3. **Performance**: N+1 queries, unnecessary allocations, missing indexes
4. **Style**: Naming, structure, consistency with project conventions
5. **Tests**: Coverage gaps, missing edge cases

Format findings as:
- 🔴 Critical — must fix
- 🟡 Warning — should fix
- 🔵 Suggestion — nice to have
```

### `/migrate` — Database Migration Generator

```markdown
Create a database migration for: $ARGUMENTS

Steps:
1. Read the current schema in src/db/schema.sql
2. Generate an alembic migration file
3. Include both upgrade and downgrade functions
4. Add appropriate indexes
5. Test the migration with `alembic upgrade head`
```

### `/doc` — Documentation Generator

```markdown
Generate documentation for $ARGUMENTS:

1. Read the source file
2. Create a corresponding .md file in docs/
3. Include:
   - Module overview
   - Function/class signatures with descriptions
   - Usage examples
   - Dependencies
4. Update docs/index.md with a link to the new doc
```

---

## Architecture

```
User types: /audit
       ↓
Claude Code finds .claude/commands/audit.md
       ↓
File contents injected as Claude's instruction
       ↓
Claude executes the instructions using available tools
       ↓
Results displayed to user
```

---

## Best Practices

1. **Keep commands focused** — Each command should do one thing well
2. **Use `$ARGUMENTS`** — Make commands reusable with arguments
3. **Reference project conventions** — Commands should follow your project's patterns
4. **Version control commands** — Commit `.claude/commands/` to share with team
5. **Test commands** — Run each command after creation to verify it works as expected

---

## Exercises

1. Create a `/audit` command that scans for security vulnerabilities in dependencies
2. Create a `/test_generator` command that accepts a file path and generates tests
3. Create a custom command specific to your project's workflow
4. Experiment with different `$ARGUMENTS` patterns (file paths vs descriptions)
