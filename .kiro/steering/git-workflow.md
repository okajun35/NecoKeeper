---
inclusion: always
---

# Git Workflow

This document defines the Git workflow for the NecoKeeper project.

## Branch Strategy

### Main Branch
- **main**: Stable branch for production environment
  - Always maintain a deployable state
  - Direct commits prohibited (Pull Requests only)

### Working Branches

#### Feature Branches (Feature Development)
- **Naming Convention**: `feature/<feature-name>`
- **Examples**:
  - `feature/public-form`
  - `feature/pdf-generation`
  - `feature/medical-records`
- **Created From**: `develop`
- **Merged To**: `develop`

#### Bug Fix Branches
- **Naming Convention**: `fix/<bug-description>`
- **Examples**:
  - `fix/404-errors`
  - `fix/timezone-issue`
  - `fix/form-validation`
- **Created From**: `develop` (or `main` for urgent fixes)
- **Merged To**: `develop` (or both `main` and `develop` for urgent fixes)

#### Refactoring Branches
- **Naming Convention**: `refactor/<target>`
- **Examples**:
  - `refactor/type-hints`
  - `refactor/error-handling`
- **Created From**: `develop`
- **Merged To**: `develop`

#### Documentation Branches
- **Naming Convention**: `docs/<content>`
- **Examples**:
  - `docs/setup-guide`
  - `docs/api-documentation`
- **Created From**: `develop`
- **Merged To**: `develop`

#### Test Branches
- **Naming Convention**: `test/<target>`
- **Examples**:
  - `test/care-log-service`
  - `test/authentication`
- **Created From**: `develop`
- **Merged To**: `develop`

## Commit Message Convention

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type (Required)
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (whitespace, formatting, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or modifying tests
- **chore**: Changes to build process or tools

### Scope (Optional)
Indicates the scope of changes:
- `auth`: Authentication related
- `api`: API endpoints
- `model`: Data models
- `service`: Business logic
- `ui`: User interface
- `test`: Tests
- `docs`: Documentation

### Subject (Required)
- Within 50 characters
- Use imperative mood ("add" not "added")
- No period at the end
- English or Japanese

### Body (Optional)
- Detailed explanation of why and what changed
- Wrap at 72 characters

### Footer (Optional)
- Reference to issue numbers
- Breaking changes notation

### Examples

```bash
# New feature
feat(api): Add public API endpoints

Implement API for care log input without authentication.
- GET /api/v1/public/animals/{id}
- POST /api/v1/public/care-logs

Closes #123

# Bug fix
fix(ui): Fix 404 errors

Fix paths for PWA icons and default images.
- Add Service Worker registration code
- Create default.svg

# Refactoring
refactor(model): Update type hints to modern syntax

- Optional[X] → X | None
- List[X] → list[X]
- Add from __future__ import annotations

# Documentation
docs: Add PWA icon setup guide

# Test
test(service): Add tests for care_log_service

Improve coverage from 68% to 85%
```

## Workflow

### 1. Feature Development Flow

```bash
# 1. Update develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Develop and commit
git add .
git commit -m "feat(scope): Add feature"

# 4. Regularly incorporate develop changes
git fetch origin
git rebase origin/develop

# 5. Push to remote
git push origin feature/new-feature

# 6. Create Pull Request (GitHub/GitLab)
# 7. Merge to develop after review
```

### 2. Bug Fix Flow

```bash
# 1. Create fix branch from develop
git checkout develop
git pull origin develop
git checkout -b fix/bug-description

# 2. Fix and commit
git add .
git commit -m "fix(scope): Fix bug"

# 3. Push and create Pull Request
git push origin fix/bug-description
```

### 3. Urgent Bug Fix (Hotfix)

```bash
# 1. Create fix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Fix and commit
git add .
git commit -m "fix(scope): Fix critical bug"

# 3. Merge to both main and develop
git checkout main
git merge hotfix/critical-bug
git push origin main

git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 4. Delete hotfix branch
git branch -d hotfix/critical-bug
```

## Commit Timing

### Commit Frequently
- Commit in small, logical units
- One commit for one change
- Commit in a working state

### When to Commit
- ✅ Added new files
- ✅ Completed part of a feature
- ✅ Fixed a bug
- ✅ Completed refactoring
- ✅ Added tests
- ✅ Updated documentation

### When NOT to Commit
- ❌ Code is not working
- ❌ Tests are failing
- ❌ Contains multiple unrelated changes
- ❌ Debug code remains

## Pre-Commit Checks (Required)

**Always run these checks before every commit**

### Batch Check with Make Command (Recommended)

```bash
# Run all checks in the same order as pre-commit
make all
```

This command executes the following in order:
1. **Lint**: Code quality check with Ruff
2. **Format**: Code formatting with Ruff
3. **Mypy**: Type checking
4. **Pytest**: Run all tests (345 tests)
5. **Prettier**: JavaScript/JSON/YAML formatting

### Individual Checks

```bash
# Basic checks only (format + lint + test)
make check

# Individual execution
make lint      # Lint check
make format    # Code formatting
make mypy      # Type checking
make test      # Run tests
make coverage  # Tests with coverage
```

### Recommended Workflow

```bash
# 1. Run all checks after code changes, before commit
make all

# 2. Commit after all checks pass
git add .
git commit -m "feat(scope): Add feature"

# 3. Push
git push origin feature/your-feature
```

### When Checks Fail

- **Lint/Format errors**: Auto-fixed, run `make all` again
- **Mypy errors**: Fix type hints
- **Test errors**: Fix tests and re-run

### pre-commit Hook

Checks run automatically on commit:

```bash
# Install pre-commit hook (first time only)
pre-commit install

# Manually check all files
pre-commit run --all-files
```

## Push Timing

### Push Regularly
- At the end of the day
- After completing important changes
- When you want to share with other developers
- To save as backup

### Pre-Push Checklist
- [ ] **Run `make all` and all checks pass** (Most important)
- [ ] All tests pass
- [ ] No lint errors
- [ ] Type checking passes
- [ ] Commit message is appropriate
- [ ] No sensitive information included

## Branch Deletion

### Delete Branch After Merge

```bash
# Delete local branch
git branch -d feature/completed-feature

# Delete remote branch
git push origin --delete feature/completed-feature
```

## .gitignore Management

Never commit the following files:

```gitignore
# Environment variables
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log

# Tests
.coverage
htmlcov/
.pytest_cache/

# Build artifacts
dist/
build/
*.egg-info/
```

## Troubleshooting

### Undo Commit

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Modify commit message
git commit --amend -m "New message"
```

### Resolve Merge Conflicts

```bash
# 1. Check conflicts
git status

# 2. Edit files to resolve conflicts
# (Remove <<<<<<<, =======, >>>>>>>)

# 3. Stage resolved files
git add <resolved-file>

# 4. Complete merge
git commit
```

### Committed to Wrong Branch

```bash
# 1. Move commit to another branch
git checkout correct-branch
git cherry-pick <commit-hash>

# 2. Remove commit from original branch
git checkout wrong-branch
git reset --hard HEAD~1
```

## Best Practices

1. **Commit small and frequently**: Avoid large changes, split into logical units
2. **Meaningful commit messages**: For your future self and other developers
3. **Push regularly**: As backup and for collaboration
4. **Keep develop up to date**: Minimize merge conflicts
5. **Write tests**: Run tests before committing
6. **Get reviews**: Ensure quality through Pull Requests
7. **Clean up branches**: Delete unnecessary branches after merge

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
