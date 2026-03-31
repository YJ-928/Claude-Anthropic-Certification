# .claude/ — Master Reference Guide

This folder is the **brain of your Claude Code workspace**. Everything here
shapes how Claude behaves, what it knows, what it can do automatically, and
how it is protected.

Use this as your starting point. Each subfolder has its own detailed README.

---

## Folder Map

```
.claude/
├── README.md              ← YOU ARE HERE
├── CLAUDE.md              ← Always-loaded workspace instructions
│
├── skills/                ← Lazy-loaded domain knowledge packs
│   ├── README.md          ← Full guide: what skills are, how to create them
│   ├── commit-message/
│   │   └── SKILL.md       ← Conventional Commits format rules
│   └── merge-request/
│       └── SKILL.md       ← MR/PR review checklist and process
│
├── agents/                ← Sub-agent definitions
│   ├── README.md          ← Full guide: what agents are, how to create them
│   ├── code-reviewer.md   ← Specialised code review agent
│   └── test-writer.md     ← Specialised test generation agent
│
├── hooks/                 ← Auto-executed lifecycle scripts
│   ├── README.md          ← Full guide: hook types, how to write them
│   ├── pre_tool_call.sh   ← Blocks dangerous commands before they run
│   ├── post_file_write.sh ← Auto-formats files after Claude writes them
│   └── session_start.sh   ← Validates environment at session open
│
└── scripts/               ← Reusable helper utilities
    ├── README.md          ← Full guide: how scripts relate to hooks/agents
    ├── run_tests.sh       ← Unified test runner (Python + JS + shell)
    ├── format_code.sh     ← Code formatter (black, prettier, shfmt)
    └── validate_env.sh    ← Pre-flight environment check
```

---

## The Five Components — One-Line Summary

| Component | File | Loaded | Job |
|---|---|---|---|
| **CLAUDE.md** | `.claude/CLAUDE.md` | Always, every session | Workspace rules & project context |
| **Skills** | `skills/<name>/SKILL.md` | On-demand, when task matches | Domain-specific instructions (commits, reviews) |
| **Agents** | `agents/<name>.md` | On-demand, spawned by main Claude | Isolated sub-tasks (review, test generation) |
| **Hooks** | `hooks/<event>.sh` | Automatically by lifecycle events | React to Claude's actions (format, block, log) |
| **Scripts** | `scripts/<name>.sh` | Called by hooks/agents/manually | Do the actual implementation work |

---

## CLAUDE.md — The Always-On File

`CLAUDE.md` is loaded **unconditionally** at the start of every session.
It is the project-level system prompt.

**Put in CLAUDE.md:**
- Project overview and purpose
- Coding standards that apply to all work
- Commit and branching rules
- Security policies
- References to skills and key commands

**Do NOT put in CLAUDE.md:**
- Very detailed domain instructions (put those in skills)
- Commands that change per-task (put those in agents)
- Anything that shouldn't always consume context

→ See the full file: [CLAUDE.md](CLAUDE.md)

---

## Skills — When to Use, When to Create

**Use skills for:** Anything that is specific to a domain and only needed some of the time.

```
"Write a commit message"      → loads commit-message skill
"Review this pull request"    → loads merge-request skill
"Explain how React works"     → no skill needed (general knowledge)
```

**Create a new skill when:**
- You find yourself giving Claude the same detailed instructions repeatedly
- You have a standard format or checklist for a recurring task
- The instructions are too detailed to put in CLAUDE.md

→ Full guide: [skills/README.md](skills/README.md)

---

## Agents — When to Use, When to Create

**Use agents for:** Isolated, focused work that shouldn't pollute the main context.

```
"Review all the changed files"    → spawn CodeReviewer agent
"Write tests for this module"     → spawn TestWriter agent
"Explore the codebase structure"  → spawn Explore agent
```

**Create a new agent when:**
- A task requires a distinct persona (security auditor, documentation writer)
- A task is purely read-only and exploratory
- You want to run tasks in parallel without cluttering the main session
- The task has a very specific, repeatable output format

→ Full guide: [agents/README.md](agents/README.md)

---

## Hooks — When to Use, When to Create

**Use hooks for:** Automating reactions to Claude's actions without thinking about it.

```
Claude writes a .py file         → post_file_write runs black + flake8
Claude tries to run rm -rf /     → pre_tool_call blocks it immediately
Session opens                     → session_start checks tools + git status
```

**Create a new hook when:**
- You want something to happen automatically every time a file type is written
- You want to enforce a safety rule on all terminal commands
- You want to log, audit, or react to specific tool usages

→ Full guide: [hooks/README.md](hooks/README.md)

---

## Scripts — When to Use, When to Create

**Use scripts for:** The actual implementation that hooks and agents call out to.

```
post_file_write.sh (hook)  →  calls run_tests.sh (script)
session_start.sh (hook)    →  calls validate_env.sh (script)
Manual terminal            →  calls format_code.sh (script)
```

**Create a new script when:**
- A hook is getting too long and the logic should be extracted
- Multiple hooks need to share the same logic
- You want to be able to run the logic manually from the terminal too

→ Full guide: [scripts/README.md](scripts/README.md)

---

## How Everything Connects — Full Flow

```
1. Session opens
        └──► session_start.sh hook fires
                  └──► calls validate_env.sh script
                            prints git status, tool availability

2. User asks: "Write a commit message for my changes"
        └──► Claude detects commit-message skill domain
                  └──► reads skills/commit-message/SKILL.md
                            follows Conventional Commits rules

3. User asks: "Review the code I wrote"
        └──► Main Claude spawns CodeReviewer agent
                  └──► agent reads changed files
                            returns structured review report

4. Claude writes a file (any file)
        └──► post_file_write.sh hook fires automatically
                  └──► calls format_code logic (black, prettier, etc.)
                            logs result to .claude/logs/

5. Claude tries to run a dangerous command
        └──► pre_tool_call.sh hook fires
                  └──► pattern matches → exits 1 → BLOCKS the command
```

---

## Quick-Start: Adding Something New

| I want to... | Do this |
|---|---|
| Add a new recurring instruction for all sessions | Edit `CLAUDE.md` |
| Teach Claude a domain-specific format or checklist | Create `skills/<name>/SKILL.md` + register it |
| Create a specialised worker for a specific task type | Create `agents/<name>.md` |
| Auto-trigger something when Claude writes a file | Edit `hooks/post_file_write.sh` |
| Block a class of dangerous commands | Edit `hooks/pre_tool_call.sh` |
| Add a reusable utility that hooks/agents can call | Create `scripts/<name>.sh` |

---

## Logs

All hooks and scripts write to `.claude/logs/` (auto-created):

```
.claude/logs/
├── pre_tool_call.log
├── post_file_write.log
├── session_start.log
├── run_tests.log
├── format_code.log
└── validate_env.log
```

Check these logs when something doesn't behave as expected.
