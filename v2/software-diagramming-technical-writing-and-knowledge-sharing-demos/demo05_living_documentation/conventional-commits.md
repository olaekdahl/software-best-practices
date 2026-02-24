# Conventional Commits Reference

A specification for adding human and machine-readable meaning to commit messages.

See: [conventionalcommits.org](https://www.conventionalcommits.org/)

## Format

```
<type>(<optional scope>): <description>

[optional body]

[optional footer]
```

## Types

| Type | Description | Bumps |
|------|-------------|-------|
| `feat` | A new feature | MINOR |
| `fix` | A bug fix | PATCH |
| `docs` | Documentation only changes | - |
| `style` | Formatting, missing semicolons, etc. | - |
| `refactor` | Code change that neither fixes a bug nor adds a feature | - |
| `perf` | Performance improvement | PATCH |
| `test` | Adding or updating tests | - |
| `build` | Changes to the build system or dependencies | - |
| `ci` | Changes to CI configuration | - |
| `chore` | Other changes that do not modify src or test files | - |

## Examples

```bash
# Feature
feat: add order cancellation within 1 hour

# Feature with scope
feat(auth): add JWT refresh token endpoint

# Bug fix
fix: prevent negative quantities in order items

# Breaking change (note the ! and footer)
feat!: change API prefix from /api/ to /v1/

BREAKING CHANGE: All API endpoints now use /v1/ prefix.
Update your client configurations accordingly.

# Performance improvement
perf: add composite index on orders(customer_id, created_at)

# Documentation
docs: update API reference for v2.2

# Multi-line with body
fix: handle race condition in inventory check

The inventory reservation was using a check-then-act pattern
without a lock. Changed to use SELECT FOR UPDATE to prevent
double-booking.

Closes #234
```

## Why Use Conventional Commits?

1. **Automated changelogs** - Tools like `standard-version` and `release-please` generate changelogs automatically
2. **Semantic versioning** - Commit types determine whether to bump MAJOR, MINOR, or PATCH
3. **Clear history** - `git log` becomes a readable project history
4. **Filtered views** - Easy to find all features, fixes, or breaking changes

## Tooling

- [commitlint](https://commitlint.js.org/) - Lint commit messages in CI
- [Commitizen](https://commitizen-tools.github.io/commitizen/) - Interactive commit message builder
- [release-please](https://github.com/googleapis/release-please) - Automated releases from conventional commits
- [standard-version](https://github.com/conventional-changelog/standard-version) - Automated versioning and changelog
