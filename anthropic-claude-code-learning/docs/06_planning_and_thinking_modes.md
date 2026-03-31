# 06 — Planning and Thinking Modes

## Overview

Claude Code provides two advanced reasoning modes that improve output quality for complex tasks. Both consume additional tokens but significantly improve results.

---

## Plan Mode

### What It Does

Plan Mode makes Claude research more files and create a detailed implementation plan **before** executing any changes.

### How to Activate

Press **Shift + Tab** twice in the Claude Code terminal.

### When to Use

- Multi-step tasks requiring wide codebase understanding
- Refactoring that spans multiple files
- Adding features that touch many modules
- Tasks where understanding dependencies is critical

### Behavior

```
Without Plan Mode:
  User request → Claude reads 1-2 files → makes changes immediately

With Plan Mode:
  User request → Claude reads 5-10+ files → creates detailed plan
  → reviews plan → executes step by step
```

### Example

```
[Plan Mode ON]
> Add user authentication to the REST API

Claude will:
1. Read existing route handlers
2. Read database models
3. Check for existing auth utilities
4. Read test structure
5. Create implementation plan:
   - Step 1: Create User model
   - Step 2: Add auth middleware
   - Step 3: Create login/register endpoints
   - Step 4: Update existing routes
   - Step 5: Write tests
6. Execute plan step by step
```

---

## Thinking Mode

### What It Does

Thinking Mode gives Claude an extended reasoning budget for complex logic. Claude spends more time "thinking" before responding.

### How to Activate

Include trigger phrases in your prompt:

- `"Ultra think"`
- `"Think deeply about this"`
- `"Think step by step"`

### When to Use

- Tricky logic or algorithms
- Debugging specific issues
- Complex data transformations
- Security analysis

### Example

```
> Ultra think: Why does this recursive function cause a stack overflow
> only when the input list has duplicate values?
```

---

## Planning vs Thinking

```
                    ┌──────────────────────────────────────┐
                    │           Task Complexity             │
                    │                                      │
                    │   Breadth ←────────────→ Depth       │
                    │                                      │
                    │   Plan Mode            Think Mode    │
                    │   ─────────            ──────────    │
                    │   Multi-file           Single issue  │
                    │   Feature addition     Bug analysis  │
                    │   Refactoring          Algorithm     │
                    │   Architecture         Security      │
                    └──────────────────────────────────────┘
```

| Aspect | Plan Mode | Thinking Mode |
|--------|-----------|---------------|
| **Focus** | Breadth | Depth |
| **Reads** | Many files | Fewer files, more analysis |
| **Best for** | Multi-step tasks | Complex single problems |
| **Activation** | Shift+Tab ×2 | "Ultra think" in prompt |
| **Token cost** | Higher (more tool calls) | Higher (longer reasoning) |

---

## Combining Modes

For the most complex tasks, combine both:

```
[Plan Mode ON]
> Ultra think: Refactor the authentication system to use JWT tokens
> instead of session cookies. Consider all security implications.
```

This gives Claude both:
- **Breadth**: Reads many files to understand the system
- **Depth**: Thinks deeply about security implications

### Cost Consideration

Both modes consume significantly more tokens. Use them when the task complexity justifies the cost.

---

## Workflow Recommendation

```
Simple task (rename variable, fix typo)
  → Normal mode

Medium task (add endpoint, write tests)
  → Plan mode OR think mode

Complex task (refactor system, debug race condition)
  → Plan mode + think mode
```

---

## Best Practices

1. **Start simple** — Try normal mode first; escalate to plan/think if results are poor
2. **Plan for breadth** — Use plan mode when the task touches many files
3. **Think for depth** — Use think mode when the logic is the hard part
4. **Combine deliberately** — Only combine modes for genuinely complex tasks
5. **Mind the cost** — Both modes increase token usage significantly

---

## Exercises

1. Try the same multi-file refactoring task with and without Plan Mode. Compare the results.
2. Ask Claude to debug a subtle logic bug with and without "Ultra think." Note the difference in analysis quality.
3. Identify three tasks from your recent work that would benefit from Plan Mode vs Thinking Mode.
