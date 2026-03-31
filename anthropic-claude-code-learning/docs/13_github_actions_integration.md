# 13 — GitHub Actions Integration

## Overview

Claude Code has an official GitHub integration that allows Claude to run inside GitHub Actions. It can review pull requests, respond to issue mentions, and perform automated development tasks.

---

## Setup Process

### Step 1: Install the GitHub App

In Claude Code terminal:

```
/install GitHub app
```

This opens a browser to install the Claude Code GitHub app on your repository.

### Step 2: Add API Key

Add your Anthropic API key as a repository secret:

- Go to **Settings → Secrets and variables → Actions**
- Add `ANTHROPIC_API_KEY` as a secret

### Step 3: Auto-Generated Actions

The installation creates two default GitHub Actions in `.github/workflows/`:

1. **Mention Support** — Responds when `@claude` is mentioned in issues or PRs
2. **PR Review** — Automatically reviews new pull requests

---

## Default Actions

### 1. Mention Support (`@claude`)

```yaml
# .github/workflows/claude-mention.yml
name: Claude Mention
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  respond:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

Usage in issues/PRs:

```
@claude Fix the failing type check in src/utils.ts
@claude Review this PR for security issues
@claude Create tests for the new authentication module
```

### 2. PR Review

```yaml
# .github/workflows/claude-pr-review.yml
name: Claude PR Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          action: review
```

---

## Customization

### Custom Instructions

Pass specific context and directions to Claude:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    action: review
    custom_instructions: |
      Focus on:
      - Security vulnerabilities (OWASP Top 10)
      - PII exposure in API responses
      - Missing input validation
      - SQL injection risks
```

### MCP Server Integration

Add MCP servers for extended capabilities (e.g., Playwright for browser testing):

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    mcp_servers: |
      {
        "playwright": {
          "command": "npx",
          "args": ["@anthropic/mcp-playwright"]
        }
      }
    allowed_tools: |
      MCP__playwright__navigate
      MCP__playwright__screenshot
      MCP__playwright__click
```

> **Important**: MCP server tools must be individually listed in `allowed_tools`. There are no shortcuts.

---

## Permissions

Claude Code in GitHub Actions requires explicit permissions:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

For MCP server tools, each tool must be individually permitted:

```yaml
allowed_tools: |
  MCP__playwright__navigate
  MCP__playwright__screenshot
  MCP__playwright__click
  MCP__playwright__fill
```

---

## Real-World Example: Infrastructure Security Review

A Terraform-defined AWS infrastructure with:
- DynamoDB table
- S3 bucket shared with external partner

When a developer adds user email to a Lambda function output:

```
Claude Code automatically:
1. Analyzes the PR diff
2. Traces data flow through infrastructure
3. Identifies DynamoDB → Lambda → S3 → External partner pipeline
4. Detects PII (email) exposure to external party
5. Comments on PR: "⚠️ This change exposes user PII to external partner"
```

---

## Advanced: Browser Testing with Playwright

```yaml
name: Claude Visual Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  visual-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start dev server
        run: |
          npm install
          npm run dev &
          sleep 5

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          custom_instructions: |
            Visit http://localhost:3000 and verify:
            1. The homepage loads without errors
            2. Navigation links work
            3. Forms submit correctly
            Create a checklist of findings.
          mcp_servers: |
            {
              "playwright": {
                "command": "npx",
                "args": ["@anthropic/mcp-playwright"]
              }
            }
          allowed_tools: |
            MCP__playwright__navigate
            MCP__playwright__screenshot
```

---

## Architecture

```
GitHub Event (PR opened, @claude mention)
       ↓
GitHub Actions Runner
       ↓
Claude Code Action (anthropics/claude-code-action@v1)
       ↓
Claude Code with GitHub-specific tools:
  - Read/comment on PRs
  - Read/comment on issues
  - Commit changes
  - Create PRs
  + Standard tools (read, write, bash, etc.)
  + MCP tools (if configured)
       ↓
Claude API
       ↓
Results posted back to GitHub
```

---

## Best Practices

1. **Start with PR review** — The highest-ROI automation
2. **Add custom instructions** — Focus Claude on your project's specific concerns
3. **Limit permissions** — Only grant the permissions Claude actually needs
4. **Test with draft PRs** — Verify the actions work correctly before relying on them
5. **Use MCP servers sparingly** — Each tool requires explicit permission listing

---

## Exercises

1. Set up the basic Claude Code GitHub Action for PR review
2. Add custom instructions focused on your project's security requirements
3. Configure a Playwright MCP server for visual testing
4. Create a GitHub Action that runs Claude on issue assignment
