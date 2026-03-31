# 10 — Hooks: Pre-tool and Post-tool Use

## Pre-tool-use Hooks — Deep Dive

Pre-tool-use hooks execute **before** a tool call and can block it. They are the primary mechanism for enforcing security policies and access controls.

---

### How Pre-tool Hooks Work

```
Claude: "I need to read .env"
       ↓
  tool_call: read(file_path=".env")
       ↓
  Pre-hook receives JSON via stdin:
  {
    "tool_name": "read",
    "tool_input": { "file_path": ".env" }
  }
       ↓
  Hook checks: file_path contains ".env"?
       ↓
  YES → exit 2 + stderr: "Blocked: .env files are protected"
       ↓
  Claude receives: "Blocked: .env files are protected"
  Claude responds: "I can't read .env files due to security restrictions."
```

### Exit Code Behavior

```javascript
// Allow the tool call
process.exit(0);

// Block the tool call (pre-hook only)
console.error("Reason for blocking");
process.exit(2);
```

---

### Example: Block Sensitive File Access

**`.claude/settings.local.json`**:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "read|grep",
        "hooks": [
          {
            "type": "command",
            "command": "node ./hooks/block_env_read.js"
          }
        ]
      }
    ]
  }
}
```

**`hooks/block_env_read.js`**:

```javascript
const fs = require("fs");

// Read tool call data from stdin
let input = "";
process.stdin.on("data", (chunk) => {
  input += chunk;
});

process.stdin.on("end", () => {
  const toolCall = JSON.parse(input);
  const filePath = toolCall.tool_input?.file_path || toolCall.tool_input?.path || "";

  if (filePath.includes(".env")) {
    console.error(`BLOCKED: Access to ${filePath} is restricted by security hook.`);
    process.exit(2);
  }

  process.exit(0);
});
```

---

## Post-tool-use Hooks — Deep Dive

Post-tool-use hooks execute **after** a tool call completes. They cannot block (the action already happened) but can provide feedback, run additional checks, or trigger follow-up actions.

---

### How Post-tool Hooks Work

```
Claude: edit(file_path="src/app.ts", ...)
       ↓
  File is edited successfully
       ↓
  Post-hook receives JSON via stdin:
  {
    "tool_name": "edit",
    "tool_input": { "file_path": "src/app.ts", ... }
  }
       ↓
  Hook runs: tsc --no-emit
       ↓
  If type errors found → stderr output sent to Claude
       ↓
  Claude reads errors and auto-fixes them
```

---

### Example: TypeScript Type Checker

**`.claude/settings.local.json`**:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "write|edit",
        "hooks": [
          {
            "type": "command",
            "command": "node ./hooks/type_check.js"
          }
        ]
      }
    ]
  }
}
```

**`hooks/type_check.js`**:

```javascript
const { execSync } = require("child_process");
const fs = require("fs");

let input = "";
process.stdin.on("data", (chunk) => {
  input += chunk;
});

process.stdin.on("end", () => {
  const toolCall = JSON.parse(input);
  const filePath = toolCall.tool_input?.file_path || "";

  // Only check TypeScript files
  if (!filePath.endsWith(".ts") && !filePath.endsWith(".tsx")) {
    process.exit(0);
  }

  try {
    execSync("npx tsc --no-emit", { encoding: "utf-8" });
    process.exit(0);
  } catch (err) {
    console.error("Type errors detected after edit:\n" + err.stdout);
    process.exit(0); // Post-hooks exit 0; feedback via stderr
  }
});
```

---

### Example: Duplicate Code Detection Hook

This advanced hook launches a second Claude instance to check for duplicate code:

```
File edited in queries/ directory
       ↓
  Post-hook detects change to watched directory
       ↓
  Launches separate Claude instance via SDK
       ↓
  Second Claude compares new code against existing code
       ↓
  If duplicate found: exit 2 + feedback
       ↓
  Original Claude receives feedback and reuses existing code
```

> **Trade-off**: Extra time and cost vs. cleaner codebase. Only watch critical directories.

---

## Matcher Patterns

The `matcher` field specifies which tools trigger the hook. Use `|` to match multiple tools:

| Matcher | Tools Matched |
|---------|--------------|
| `read` | `read` only |
| `read\|grep` | `read` and `grep` |
| `write\|edit` | `write` and `edit` |
| `bash` | `bash` only |
| `.*` | All tools |

---

## Discovering Tool Names

To find the exact tool names Claude Code uses, ask Claude directly:

```
> What tools do you have available? List their names.
```

Common tool names: `read`, `write`, `edit`, `bash`, `grep`, `glob`, `ls`

---

## Best Practices

1. **Pre-hooks for security** — Block access to secrets, credentials, production configs
2. **Post-hooks for quality** — Type checking, formatting, linting, testing
3. **Keep hooks fast** — Slow hooks degrade the interactive experience
4. **Log blocked operations** — Maintain audit trail of blocked tool calls
5. **Test hooks by asking Claude to read a blocked file** — Verify blocking works

---

## Exercises

1. Write a pre-hook that blocks write access to any file in the `migrations/` directory
2. Write a post-hook that runs `black` (Python formatter) after any `.py` file is edited
3. Design a post-hook that runs the test suite for the specific module that was edited
4. Explain why post-hooks cannot block tool execution
