# Skills — Reference Guide

## What is a Skill?

A **Skill** is a file containing domain-specific instructions that Claude loads
**on demand** — only when the task at hand matches the skill's domain.

Think of it as a specialised knowledge pack. Instead of Claude keeping all
possible instructions in memory all the time (which wastes context), skills are
fetched only when relevant. This keeps every session lean and focused.

---

## How Skills Are Different From CLAUDE.md

| | `CLAUDE.md` | `skills/` |
|---|---|---|
| **When loaded** | Always — every session, unconditionally | Only when the task matches the skill domain |
| **Purpose** | Persistent workspace rules and context | Domain-specific deep instructions |
| **Token cost** | Constant — always in context | Zero unless triggered |
| **Best for** | Coding standards, project overview, security rules | Commit formats, review checklists, API guides |

---

## How a Skill Gets Triggered (Loading Mechanism)

1. You make a request — e.g. *"Write a commit message for this change"*
2. Claude detects the task matches the `commit-message` skill domain
3. Claude calls `readFile` on the skill's `SKILL.md` path
4. Claude reads the instructions **right then**, in that turn
5. Claude follows those instructions to complete the task

The skill declaration lives in VS Code's `customizationsIndex` (configured in
your VS Code settings). Each entry tells Claude:
- the skill's **name** (identifier)
- the skill's **description** (what domain it covers — this is what Claude pattern-matches against)
- the **file path** to load when triggered

```
skill: commit-message
  description: "Commit Message Format"
  file: .claude/skills/commit-message/SKILL.md
```

---

## Anatomy of a SKILL.md File

Every SKILL.md has two parts:

### 1. YAML Frontmatter (required)

```yaml
---
name: commit-message          # unique identifier, no spaces
description: Commit Message Format  # one-line summary Claude uses for matching
---
```

### 2. Instruction Body (the actual content)

Everything after the frontmatter is the instruction set Claude reads and follows.
Write it in plain Markdown. Be specific — Claude will follow it literally.

```markdown
# Commit Message Format

Always use Conventional Commits:
- feat: for new features
- fix: for bug fixes

## Structure
<type>(<scope>): <summary>
```

---

## Skills in This Workspace

| Skill Name | File | Triggered When... |
|---|---|---|
| `commit-message` | `commit-message/SKILL.md` | Asked to write, format, or review a git commit message |
| `merge-request` | `merge-request/SKILL.md` | Asked to review a GitHub/GitLab pull request or MR |

---

## How to Create a New Skill

### Step 1 — Create the folder and file

```
.claude/skills/
└── your-skill-name/
    └── SKILL.md
```

```bash
mkdir -p .claude/skills/your-skill-name
touch .claude/skills/your-skill-name/SKILL.md
```

### Step 2 — Write the SKILL.md

```markdown
---
name: your-skill-name
description: One sentence describing when this skill should activate
---

# Your Skill Title

[All your domain-specific instructions go here]

## Section 1
...

## Section 2
...
```

### Step 3 — Register it in VS Code settings

Open your VS Code `settings.json` (or the relevant customisation config) and add:

```json
{
  "github.copilot.chat.skills": [
    {
      "name": "your-skill-name",
      "description": "One sentence describing when this skill should activate",
      "file": ".claude/skills/your-skill-name/SKILL.md"
    }
  ]
}
```

Once registered, Claude will automatically load it when the task matches.

---

## What Makes a Good Skill?

| Principle | Detail |
|---|---|
| **Narrow domain** | One skill = one topic. Don't combine "commit messages + code review" in one skill |
| **Prescriptive** | Write rules, not suggestions. "Always use X" not "Consider using X" |
| **Structured** | Use headings, tables, code blocks. Claude reads structure well |
| **Concrete examples** | Show examples of correct and incorrect output |
| **Actionable** | Every instruction should result in an observable behaviour |

---

## Skill Writing Template

Copy this to start a new skill fast:

```markdown
---
name: SKILL-NAME
description: TRIGGER DESCRIPTION — one clear sentence
---

# SKILL TITLE

## When This Skill Applies
[Describe the exact scenario when this skill is relevant]

## Rules
1. Rule one
2. Rule two
3. Rule three

## Structure / Format
[Show the exact format, template, or schema to follow]

## Examples

### Good Example
[Show a correct example]

### Bad Example
[Show what NOT to do and why]

## Edge Cases
[Any special conditions or exceptions]
```

---

## Common Mistakes to Avoid

- **Empty SKILL.md** — A file with only frontmatter gives Claude nothing to follow
- **Vague description** — If the description is too broad, the skill may fire on unrelated tasks
- **Too large** — Keep skills focused. A 2000-line skill is hard for Claude to apply correctly
- **Forgetting to register** — Creating the file alone isn't enough; it must be in the customisationsIndex
- **No examples** — Abstract rules without examples lead to inconsistent output

---

## Quick Reference

```
Triggering:   User request matches skill description → Claude reads SKILL.md → follows it
Location:     .claude/skills/<name>/SKILL.md
Required:     YAML frontmatter (name + description) + instruction body
Registration: Add to VS Code settings customisationsIndex
Token cost:   0 unless triggered
```
