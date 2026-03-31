---
name: commit-message
description: Commit Message Format
---

# Commit Message Format — Conventional Commits

All commit messages in this workspace **must** follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

---

## Structure

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

- **type** — required, must be one of the types listed below
- **scope** — optional, the module or area of the codebase affected (in parentheses)
- **short summary** — required, imperative tense, lowercase, no period at the end, max 72 chars
- **body** — optional, explain *what* and *why*, not *how*. Wrap at 100 chars
- **footer** — optional, reference issue/PR numbers or mark breaking changes

---

## Types

| Type | When to use |
|---|---|
| `feat` | A new feature or capability |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructured — no new feature or bug fix |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Build, tooling, dependency updates |
| `ci` | Changes to CI/CD pipeline configuration |
| `revert` | Reverts a previous commit |

---

## Breaking Changes

Breaking changes must be indicated in the **footer** with `BREAKING CHANGE:` or by appending `!` after the type/scope:

```
feat(api)!: remove deprecated /v1 endpoints

BREAKING CHANGE: /v1/users and /v1/orders have been removed.
Migrate to /v2 equivalents before upgrading.
```

---

## Examples

```
feat(auth): add JWT token refresh logic
```

```
fix(api): handle null response from payment gateway

The payment gateway occasionally returns null on timeout.
Added a fallback to retry once before raising an error.

Closes #142
```

```
docs(readme): update installation steps for Linux
```

```
chore(deps): bump requests from 2.28.0 to 2.31.0
```

```
test(auth): add unit tests for token expiry edge cases
```

---

## Rules

1. Never use past tense — use imperative: `add`, not `added`
2. Never capitalize the first word of the summary
3. Never end the summary line with a period
4. Scope must be lowercase and use hyphens for multi-word scopes: `(user-auth)`
5. One commit = one logical change. Do not bundle unrelated changes
6. Reference relevant GitHub issues in the footer: `Closes #45`, `Refs #102`