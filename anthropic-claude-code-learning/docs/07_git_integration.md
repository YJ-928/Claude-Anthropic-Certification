# 07 — Git Integration

## Overview

Claude Code integrates directly with Git, allowing it to stage changes, write commit messages, and interact with version control as part of its workflow.

---

## Core Git Capabilities

### Staging and Committing

Claude Code can:
- Stage modified files with `git add`
- Generate descriptive commit messages based on the changes made
- Execute `git commit` with appropriate messages

```
> Commit the changes I just made with a descriptive message

Claude will:
1. Run `git diff --staged` or `git diff` to see changes
2. Analyze what was modified
3. Write a descriptive commit message
4. Execute `git add` and `git commit`
```

### Commit Message Quality

Claude writes commit messages that describe **what** changed and **why**:

```
feat: add input validation to user registration endpoint

- Add email format validation using regex pattern
- Add password strength requirements (min 8 chars, mixed case)
- Return 422 with specific error messages for invalid input
- Add tests for validation edge cases
```

---

## Screenshot-Driven Workflow

Claude Code supports pasting screenshots to show visual issues:

```
Workflow:
1. Take screenshot of problematic UI element
2. Press Ctrl+V (not Cmd+V on macOS) to paste in Claude Code
3. Describe the desired change
4. Claude analyzes the screenshot and makes changes
5. Review and accept the implementation
```

---

## Git Workflow with Claude Code

```
┌────────────────────────────────────┐
│  1. Start feature work             │
│     > Add pagination to user list  │
├────────────────────────────────────┤
│  2. Claude implements changes      │
│     - Reads existing code          │
│     - Makes edits                  │
│     - Runs tests                   │
├────────────────────────────────────┤
│  3. Review changes                 │
│     > Show me what changed         │
│     (Claude runs git diff)         │
├────────────────────────────────────┤
│  4. Commit                         │
│     > Commit these changes         │
│     (Claude writes commit msg)     │
├────────────────────────────────────┤
│  5. Continue or switch tasks       │
│     > /clear (if switching tasks)  │
└────────────────────────────────────┘
```

---

## Best Practices

1. **Review before committing** — Always review Claude's changes with `git diff` before accepting commits
2. **Use Plan Mode for large changes** — Activate plan mode for changes spanning many files
3. **Leverage screenshots** — Paste screenshots of UI bugs for visual context
4. **Commit incrementally** — Ask Claude to commit after each logical unit of work
5. **Don't force-push** — Claude will not (and should not) force-push by default

---

## Exercises

1. Make a code change with Claude Code and have it generate a commit message
2. Use the screenshot paste workflow to fix a UI alignment issue
3. Have Claude review a diff and explain what changed
