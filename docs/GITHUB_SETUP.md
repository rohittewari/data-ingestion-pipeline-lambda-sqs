# GitHub CI/CD Setup Instructions

This guide walks you through setting up GitHub for Continuous Integration (CI) with your project.

## Prerequisites

- GitHub account
- Repository created on GitHub
- Local git configured on your machine

## Step-by-Step Setup

### 1. Initialize Git (If Not Already Done)

```powershell
cd c:\Rohit\1_Interview\FINRA_INTERVIEW
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 2. Add GitHub as Remote

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual values:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Verify:
```powershell
git remote -v
```

### 3. Create Initial Commit

```powershell
git add .
git commit -m "Initial commit: Phase 0 foundation setup"
```

### 4. Push to GitHub

```powershell
git branch -M main
git push -u origin main
```

### 5. Verify CI Workflow File Exists

The CI workflow should already exist at:
```
.github/workflows/ci.yml
```

This file contains:
- **Lint check**: `ruff check .`
- **Unit tests**: `pytest -q`
- **Triggers**: On pull requests and pushes to `main`

### 6. Push Workflow to GitHub

```powershell
git add .github/workflows/ci.yml
git commit -m "Add GitHub Actions CI workflow"
git push origin main
```

### 7. Verify CI is Running

1. Go to your GitHub repository
2. Click **Actions** tab
3. You should see the `ci` workflow listed
4. Click on it to see the latest run details

---

## How to Use CI in Your Workflow

### Creating a Pull Request

```powershell
# Create a feature branch
git checkout -b feature/my-feature

# Make your changes
# ... edit files ...

# Commit and push
git add .
git commit -m "Add new feature"
git push origin feature/my-feature
```

### CI Automatically Runs

When you push to a feature branch:
1. GitHub creates a PR
2. **Actions** tab shows the workflow running
3. CI checks:
   - ✅ **Linter** - Code quality and style
   - ✅ **Tests** - All unit tests pass

### Merge Conditions

You can require all checks to pass before merging:

1. Go to **Settings** → **Branches**
2. Select **main** branch
3. Enable **Require status checks to pass before merging**
4. Select `lint-and-test` workflow

Now you can only merge PRs when CI passes! ✅

---

## Troubleshooting

### CI Workflow Not Showing

**Problem**: Actions tab is empty

**Solution**:
1. Ensure `.github/workflows/ci.yml` exists in your main branch
2. Push the workflow file to GitHub:
   ```powershell
   git push origin main
   ```
3. Refresh the Actions tab

### Workflow Fails - Lint Issues

**Problem**: `ruff check .` fails

**Solution**: Fix locally before pushing
```powershell
ruff check .
ruff format .  # Auto-fix formatting
```

### Workflow Fails - Test Failures

**Problem**: `pytest -q` fails

**Solution**: 
```powershell
pytest -v  # Run locally to see details
# Fix the failing tests
pytest     # Re-run to verify
```

---

## What the CI Workflow Does

**File**: `.github/workflows/ci.yml`

| Step | Command | Purpose |
|------|---------|---------|
| Checkout | `checkout@v4` | Gets your code |
| Python Setup | `setup-python@v5` | Installs Python 3.11 |
| Dependencies | `pip install -r requirements-dev.txt` | Installs dev packages |
| Lint | `ruff check .` | Checks code quality |
| Tests | `pytest -q` | Runs unit tests |

**Triggers**:
- ✅ Every pull request
- ✅ Every push to `main` branch

---

## Next Steps

1. Push your code to GitHub following steps 1-6 above
2. Create a test pull request from a feature branch
3. Watch CI run automatically
4. Merge when all checks pass

---

## Quick Reference Commands

```powershell
# Check git status
git status

# Create feature branch
git checkout -b feature/name

# Commit changes
git add .
git commit -m "Your message"

# Push to GitHub
git push origin feature/name

# View logs
git log --oneline

# Delete feature branch (after merge)
git branch -d feature/name
```

---

For more info on GitHub Actions, see: https://github.com/features/actions
