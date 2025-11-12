# Technology Stack

## Language
- **Python 3.x**

## Package Management
The project supports multiple Python package managers:
- UV (recommended based on .gitignore)
- Poetry
- Pipenv
- PDM
- Pixi

## Development Tools
- **Ruff**: Python linter and formatter
- **mypy**: Static type checker
- **pytest**: Testing framework (inferred from .gitignore)

## Common Commands
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies (if using UV)
uv pip install -r requirements.txt

# Run tests
pytest

# Lint and format
ruff check .
ruff format .

# Type checking
mypy .
```

## Environment
- Environment variables stored in `.env` (gitignored)
- Virtual environments in `.venv` directory
