---
name: merge-request
description: To review a merge request on github or gitlab
---

# Merge Request Review — Checklist & Process

When asked to review a merge request (MR/PR) on GitHub or GitLab, follow this structured process.

---

## Step 1 — Understand the Change

- Read the MR title and description fully
- Identify the **intent**: What problem does this solve?
- Check if the MR is linked to an issue or ticket
- Review which files changed and how many lines were modified

---

## Step 2 — Code Review Checklist

### Correctness
- [ ] Does the code do what the description says?
- [ ] Are edge cases handled (null, empty, overflow)?
- [ ] Are error conditions properly caught and reported?
- [ ] Does it handle concurrency/race conditions if applicable?

### Security (OWASP Top 10)
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Input validation at all system boundaries
- [ ] No SQL injection risk (use parameterized queries)
- [ ] No XSS vulnerabilities (escape output in HTML contexts)
- [ ] Access control enforced at every endpoint
- [ ] Sensitive data not logged or exposed in responses

### Code Quality
- [ ] Functions are small and single-responsibility
- [ ] No duplicate logic — DRY principle applied
- [ ] Variable and function names are descriptive
- [ ] No dead code or commented-out blocks left
- [ ] Complex logic has explanatory comments

### Tests
- [ ] New functionality has corresponding unit tests
- [ ] Existing tests still pass
- [ ] Edge cases and error paths are tested
- [ ] Test names clearly describe what they verify

### Documentation
- [ ] Public API changes are reflected in docs
- [ ] Breaking changes are clearly documented
- [ ] CHANGELOG or release notes updated if needed

### Dependencies
- [ ] No unnecessary new dependencies added
- [ ] Any new dependency is actively maintained and license-compatible
- [ ] No vulnerable versions introduced (check CVEs)

---

## Step 3 — Provide Structured Feedback

Organize feedback by severity:

| Label | Meaning |
|---|---|
| `BLOCKING` | Must be fixed before merge — correctness or security issue |
| `SUGGESTION` | Improvement that would make code better but is not required |
| `QUESTION` | Needs clarification — may or may not require change |
| `NITPICK` | Minor style or readability — author's discretion |
| `PRAISE` | Good code worth acknowledging |

---

## Step 4 — Final Recommendation

End the review with one of:

- **APPROVE** — Ready to merge as-is
- **APPROVE WITH SUGGESTIONS** — Mergeable, but suggestions worth considering
- **REQUEST CHANGES** — Must address BLOCKING items before merge
- **NEEDS DISCUSSION** — Design or scope questions must be resolved first

---

## Example Review Output

```
## MR Review: feat(auth) — Add OAuth2 login flow

**Summary:** Adds Google and GitHub OAuth2 login. Overall solid implementation.

### Issues Found

[BLOCKING] `src/auth/oauth.py:45`
The `state` parameter is not validated on callback, making this vulnerable
to CSRF attacks. Validate that the returned state matches the session state.

[SUGGESTION] `src/auth/oauth.py:78`
Consider extracting the token exchange logic into a separate `exchange_code()`
function to improve readability and testability.

[NITPICK] `src/auth/utils.py:12`
Variable `d` could be renamed to `decoded_token` for clarity.

[PRAISE] Error handling in `handle_callback()` is thorough and clean.

### Recommendation: REQUEST CHANGES
Address the CSRF vulnerability before merging.
```
