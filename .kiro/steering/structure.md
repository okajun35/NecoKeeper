# Project Structure

## Root Directory
```
NecoKeeper/
├── .git/              # Git version control
├── .kiro/             # Kiro AI assistant configuration
│   ├── settings/      # Kiro settings (MCP, etc.)
│   ├── specs/         # Feature specifications
│   └── steering/      # AI guidance rules
├── .gitignore         # Git ignore patterns (Python-focused)
└── README.md          # Project documentation
```

## Conventions

### Python Code Organization
- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Keep modules focused and single-purpose

### Testing
- Test files in `.pytest_cache/` (gitignored)
- Coverage reports in `htmlcov/` and `.coverage` (gitignored)

### Documentation
- Sphinx documentation in `docs/_build/` (gitignored)
- Keep README.md updated with project overview

### Ignored Patterns
- Python bytecode (`__pycache__/`, `*.pyc`)
- Distribution files (`dist/`, `build/`, `*.egg-info/`)
- Virtual environments (`.venv/`, `venv/`, `env/`)
- IDE settings (`.vscode/`, `.idea/`)
- Environment files (`.env`)
- Cache directories (`.ruff_cache/`, `.mypy_cache/`)
