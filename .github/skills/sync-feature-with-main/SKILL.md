---
title: Sync Feature Branch with Main
description: Pull latest changes from remote main, then merge into any feature branch to keep feature in sync with upstream changes. Handles tracking setup and merge conflicts.
applyTo: "*.md, *.py, Dockerfile, pyproject.toml"
---

# Sync Feature Branch with Main

## Purpose

Keep a feature branch up to date with the latest changes from `main` (e.g., after a PR merge or teammate push). This workflow:

- Pulls fresh changes from remote `main`
- Merges them into your feature branch
- Handles tracking setup and conflict resolution

Use this when:

- Main has new commits and you need to integrate them
- You want to test feature compatibility with latest main
- Before opening/rebasing a PR to avoid conflicts later
- Collaborators have pushed updates to main

## Prerequisites

- Git is initialized and remotes are configured
- You have a local feature branch checked out (or can specify one)
- No uncommitted changes (stash if needed)

## Workflow Steps

### 1. Checkout and Pull Main

```bash
git checkout main
git branch --set-upstream-to=origin/main main    # (optional, if tracking not set)
git pull
```

**What this does:**

- Switches to `main` branch
- Establishes tracking (skippable if already done)
- Fetches and merges remote changes

**Exit signals:**

- ✅ `Fast-forward` or `Already up to date.` → clean pull
- ❌ `Connection refused` / `fatal: unable to access` → network issue; retry or check remote

### 2. Return to Feature Branch

```bash
git checkout <FEATURE_BRANCH>
```

Replace `<FEATURE_BRANCH>` with your branch name (e.g., `feature/project-setup`).

### 3. Merge Main into Feature

```bash
git merge main
```

**Possible outcomes:**

#### ✅ Clean Merge

```
Updating 7b360a7..fcf357b
Fast-forward
 README.md | 2 +-
 1 changed, 1 insertion(+), 1 deletion(-)
```

→ Done. Continue with your work.

#### ⚠️ Merge Conflict

If conflicts occur:

```
CONFLICT (content): Merge conflict in <file>
Automatic merge failed; fix conflicts and then commit the result.
```

**Resolution steps:**

1. **Identify conflicted files:**

   ```bash
   git status
   ```

   Files with `both modified` are in conflict.

2. **Open and resolve** each file:
   - Look for conflict markers: `<<<<<<<`, `=======`, `>>>>>>>`
   - Keep desired changes, remove markers
   - Save

3. **Stage resolved files:**

   ```bash
   git add <file>
   # or add all:
   git add .
   ```

4. **Complete the merge:**

   ```bash
   git commit -m "merge: integrate main into <FEATURE_BRANCH>"
   ```

5. **Verify:**
   ```bash
   git log --oneline -3
   ```
   Should show your merge commit at the top.

#### ❌ Abort If Needed

If merge is messy:

```bash
git merge --abort
```

Then troubleshoot or ask for help.

## Decision Tree

```
Is main ahead of feature?
  ├─ YES
  │  ├─ Checkout main → Pull → Checkout feature → Merge
  │  └─ Result: Clean merge or conflict (see above)
  └─ NO
     └─ Feature is already in sync or ahead; skip
```

## After Sync

- Run tests to ensure compatibility:
  ```bash
  uv run pytest
  ```
- Push (optional):
  ```bash
  git push origin <FEATURE_BRANCH>
  ```
- Continue development

## Common Pitfalls

| Issue                             | Cause                      | Fix                                                         |
| --------------------------------- | -------------------------- | ----------------------------------------------------------- |
| `fatal: not a git repository`     | Wrong directory            | `cd` to repo root                                           |
| `Permission denied`               | SSH key or credentials     | Check `git remote -v` and SSH setup                         |
| Merge conflicts feel overwhelming | Too many divergent changes | `git merge --abort`, rebase strategy, or pair with reviewer |
| Accidentally merged wrong branch  | Typo or checkout error     | `git reset --hard HEAD~1` (loses merge; use cautiously)     |
| Tracking branch not set           | First sync to remote       | Use `git branch --set-upstream-to=origin/main main`         |

## Example Prompts

To use this skill, try:

- "Sync feature/my-feature with main"
- "Pull latest main and merge into my feature branch"
- "I need to integrate recent changes from main into feature/project-setup"
- "Help me resolve merge conflicts after syncing with main"

## Related Skills / Next Steps

- **Branch Protection & PR Workflow** — After syncing, submit a PR for review
- **Conflict Resolution (Advanced)** — For complex 3-way merges or rebase workflows
- **Git Troubleshooting** — For undo/recover scenarios

---

**Last updated:** 2026-06-26
