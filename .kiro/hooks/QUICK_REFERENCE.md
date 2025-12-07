# Kiro Hooks Quick Reference

Cheat sheet for ready-to-use commands and workflows.

## 🚀 Frequently Used Commands

### Pre-commit Checks
```bash
# Run all quality checks
make all

# Or run individually
make lint       # Lint checks
make format     # Code formatting
make type-check # Type checks
make test       # Run tests
```

### Coverage Verification
```bash
# Measure coverage
pytest --cov=app --cov-report=term-missing

# Generate HTML report
pytest --cov=app --cov-report=html

# Open report
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
start htmlcov/index.html     # Windows
```

### Care Log Registration
```bash
# Manual registration
PYTHONPATH=. python scripts/hooks/register_care_logs.py tmp/json/file.json

# PDF conversion
python scripts/hooks/pdf_to_image.py tmp/pdf/file.pdf --use-pymupdf
```

---

## 📋 Hook List (for Copy & Paste)

### 1. Pre-Commit Quality Gate
```
Run: Ctrl+Shift+P → "Pre-Commit Quality Gate"
Purpose: Run all quality checks before commit
Time: 30-60 seconds
```

### 2. Test Coverage Analyzer
```
Run: Ctrl+Shift+P → "Test Coverage Analyzer"
Purpose: Coverage analysis and improvement suggestions
Time: 10-30 seconds
```

### 3. Register Care Logs (Manual)
```
Run: Right-click tmp/json/*.json → "Register Care Logs (Manual)"
Purpose: Manual care log registration
Time: 1-5 seconds
```

### 4. Register Care Logs (Auto)
```
Run: Save to tmp/json/auto.json to run automatically
Purpose: Automatic care log registration
Time: 1-5 seconds
```

### 5. PDF to Image Converter
```
Run: Right-click tmp/pdf/*.pdf → "PDF to Image Converter"
Purpose: Convert PDF to images
Time: 5-30 seconds
```

---

## 🔄 Typical Workflows

### Workflow 1: New Feature Development

```bash
# 1. Create branch
git checkout -b feature/new-feature

# 2. Implement code
# ... coding ...

# 3. Quality checks
make all

# 4. Coverage verification
pytest --cov=app --cov-report=term-missing

# 5. Commit
git add .
git commit -m "feat(scope): add new feature"

# 6. Push
git push origin feature/new-feature
```

### Workflow 2: OCR Care Log Import

```bash
# 1. Place PDF
cp /path/to/care-log.pdf tmp/pdf/

# 2. PDF → Image conversion (right-click or command)
python scripts/hooks/pdf_to_image.py tmp/pdf/care-log.pdf --use-pymupdf

# 3. Image → JSON (via Kiro chat)
# [Attach image]
# "This is the record for cat ID 12 from November 14 to 23, 2024.
#  Please convert it to JSON and save it to tmp/json/care_log_20241114.json."

# 4. JSON → DB (right-click or automatic)
# Right-click tmp/json/care_log_20241114.json
# → "Register Care Logs (Manual)"
```

### Workflow 3: Test Coverage Improvement

```bash
# 1. Check current status
pytest --cov=app --cov-report=html

# 2. Detailed analysis (run hook)
# Ctrl+Shift+P → "Test Coverage Analyzer"

# 3. Add missing tests
# Edit tests/test_xxx.py

# 4. Re-measure
pytest --cov=app --cov-report=term-missing

# 5. Verify improvement
# Check if coverage has improved
```

---

## 🐛 Troubleshooting Quick Reference

| Problem | Solution |
|--------|----------|
| Hook does not run | Check `"enabled": true` in `.kiro.hook` file |
| API authentication error | Check `NECOKEEPER_ADMIN_USERNAME/PASSWORD` in `.env` |
| Module error | `source .venv/bin/activate` → `pip install -r requirements.txt` |
| Test failure | Run `pytest tests/test_xxx.py -v` for details |
| Mypy error | Add type hints: `def func(x: int) -> str:` |
| JSON error | Validate with `python -m json.tool tmp/json/file.json` |
| PDF error | Install library with `pip install PyMuPDF` |
| Permission error | Grant execute permission with `chmod +x scripts/hooks/*.py` |

---

## 📊 Coverage Targets

| Layer | Target | Current | Status |
|-------|--------|---------|--------|
| Domain layer (models/) | 90%+ | 92% | ✅ |
| Service layer (services/) | 80%+ | 75% | ⚠️ |
| API layer (api/) | 70%+ | 78% | ✅ |
| Authentication layer (auth/) | 80%+ | 85% | ✅ |
| Utility layer (utils/) | 70%+ | 65% | ⚠️ |
| **Overall** | **70%+** | **80.99%** | ✅ |

---

## 🔑 Environment Variable Checklist

```bash
# Verify that the following are set in the .env file
cat .env

# Required variables
NECOKEEPER_API_URL=http://localhost:8000
NECOKEEPER_ADMIN_USERNAME=admin
NECOKEEPER_ADMIN_PASSWORD=your_password

# Optional
AUTOMATION_API_ENABLED=true
AUTOMATION_API_KEY=your_32_character_key
```

---

## 📁 Directory Structure

```
tmp/
├── pdf/                    # PDF input
├── pdfs/                   # PDF input (alternative)
├── images/                 # Converted images
└── json/                   # JSON data
   ├── auto.json           # For automatic registration
   └── processed/          # Processed files
```

---

## 🎯 Commit Message Examples

```bash
# New feature
git commit -m "feat(api): add new endpoint"

# Bug fix
git commit -m "fix(ui): fix validation in login form"

# Refactoring
git commit -m "refactor(service): update type hints to modern syntax"

# Add tests
git commit -m "test(mcp): add tests for MCP tools"

# Documentation
git commit -m "docs: add Kiro hooks guide"

# Style
git commit -m "style: apply Ruff formatting"

# Performance
git commit -m "perf(db): optimize queries"

# Build / chores
git commit -m "chore: update dependencies"
```

---

## 🔗 Frequently Used Links

- [Complete Guide](./HOOKS_GUIDE.md)
- [OCR Workflow](./README.md)
- [API Specification](../../app/api/automation/README.md)
- [MCP Integration](../../app/mcp/README.md)
- [Test Guide](../../tests/README.md)

---

## 💡 Tips

### For Efficient Development

1. **Always run `make all` before committing**
   - Catch quality issues early
   - Prevent CI/CD failures

2. **Analyze coverage weekly**
   - Detect missing tests early
   - Prevent technical debt from accumulating

3. **Customize hooks**
   - Adapt to project-specific needs
   - Optimize your workflow

4. **Check the logs**
   - Use `logs/ocr-import.log` for detailed investigation
   - Makes it easier to identify root causes of errors

5. **Manage environment variables properly**
   - Use `.env.example` as a template
   - Do not commit secrets to Git

---

**For printing**: You can save this page as PDF and keep it at your desk for quick reference.

**Last Updated**: November 30, 2024
