# 15 — Best Practices

## Summary of Claude Code Best Practices

This document consolidates the key practices for effective use of Claude Code across all topics.

---

## 1. Context Management

### DO
- Use `/init` on new projects to generate a Claude.md file
- Reference critical files in Claude.md (schemas, configs, key modules)
- Use `@file` mentions for targeted context
- Use `#` memory mode to prevent repeated mistakes
- Use `/compact` when conversations get cluttered but context is valuable
- Use `/clear` when switching to unrelated tasks

### DON'T
- Dump entire file contents into Claude.md
- Include frequently changing information in Claude.md
- Let conversations grow indefinitely without compacting

---

## 2. Tool Use

### DO
- Trust Claude's tool chaining — let it iterate through read → plan → write → test
- Set timeouts on command execution
- Log tool calls for debugging and auditing
- Use hooks to enforce security policies on tool access

### DON'T
- Execute shell commands without reviewing what Claude proposes
- Allow unrestricted tool access in production environments
- Ignore tool call errors

---

## 3. Planning and Thinking

```
Task Complexity → Mode Selection

Simple (rename, typo fix)     → Normal mode
Medium (add endpoint, tests)   → Plan mode OR think mode
Complex (refactor, debug race) → Plan mode + think mode
```

### DO
- Start with normal mode; escalate if results are poor
- Use plan mode for broad, multi-file tasks
- Use "Ultra think" for complex logic and deep debugging
- Combine modes for genuinely complex tasks

### DON'T
- Use plan mode for trivial changes (wastes tokens)
- Forget that both modes increase token cost

---

## 4. Hooks

### DO
- Use pre-hooks for security (blocking sensitive file access)
- Use post-hooks for quality (formatting, type-checking, testing)
- Keep hooks fast
- Restart Claude Code after hook changes
- Test hooks by triggering the exact tool they intercept

### DON'T
- Write slow hooks that delay every tool call
- Forget to handle both `file_path` and `path` in hook scripts
- Use exit code 2 in post-hooks (it has no effect)

---

## 5. Custom Commands

### DO
- Create commands for repetitive tasks (/audit, /test, /review)
- Use `$ARGUMENTS` for flexible commands
- Keep commands focused on a single purpose
- Commit `.claude/commands/` to version control

### DON'T
- Create overly broad commands that try to do everything
- Forget to restart Claude Code after adding commands

---

## 6. SDK Usage

### DO
- Default to read-only permissions
- Explicitly list allowed tools when writes are needed
- Use SDK for automated pipelines (CI/CD, batch processing)
- Handle SDK errors gracefully

### DON'T
- Grant blanket tool access
- Use SDK where the interactive terminal would be better
- Ignore return codes

---

## 7. GitHub Actions

### DO
- Start with automated PR review (highest ROI)
- Add custom instructions focused on your project's concerns
- Test with draft PRs first
- List MCP permissions individually

### DON'T
- Grant more permissions than necessary
- Skip testing the action before relying on it
- Assume MCP tools are auto-approved

---

## 8. Security

| Practice | Description |
|----------|-------------|
| Hook-based access control | Block access to `.env`, credentials, private keys |
| Read-only SDK defaults | Only enable writes when needed |
| Direct code search | Claude searches code directly, not via external indexing |
| Permission listing | Explicitly list all allowed tools (no wildcards) |
| Audit logging | Log tool calls for review |
| PII detection | Use Claude in PR reviews to catch PII exposure |

---

## 9. Coding Style with Claude

### DO
- Specify coding conventions in Claude.md
- Use type hints (Claude respects them)
- Keep modules small and focused
- Write tests alongside implementation

### DON'T
- Accept generated code without review
- Skip the test phase
- Let Claude commit directly to main/production branches

---

## 10. Workflow Summary

```
New Project Setup:
  1. /init → generate Claude.md
  2. Review and edit Claude.md
  3. Set up hooks for security (.env protection)
  4. Create custom commands for common tasks
  5. Install relevant MCP servers

Daily Workflow:
  1. Start Claude Code
  2. Use @file for targeted context
  3. Normal mode for simple tasks
  4. Plan mode for multi-file changes
  5. Think mode for complex logic
  6. /compact when conversation gets long
  7. /clear when switching tasks
  8. Let Claude commit with descriptive messages

Automation:
  1. Set up GitHub Actions for PR review
  2. Use SDK in CI/CD pipelines
  3. Post-tool hooks for formatting and testing
  4. Pre-tool hooks for security enforcement
```

---

## Key Principle

> Claude Code is a **flexible assistant that grows with your needs** through tool expansion (MCP servers), context management (Claude.md), and workflow automation (hooks, commands, SDK, GitHub Actions).

The more you invest in setting up context and guardrails, the more effective and safe Claude Code becomes.
