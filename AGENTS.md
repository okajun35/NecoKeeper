# Repository Guidelines
本リポジトリに関するやり取りは日本語で行ってください。
作業開始前に`.kiro/steering/`配下のガイドを必ず読み、指示に従ってください。

## Project Structure & Module Organization
- `app/` is the FastAPI application: API routes in `app/api/`, models in `app/models/`, services in `app/services/`, templates in `app/templates/`, static assets in `app/static/`, and i18n files in `app/locales/`.
- `tests/` contains pytest suites organized by domain (e.g., `tests/api/`, `tests/services/`).
- `alembic/` and `alembic.ini` hold database migration configuration.
- `data/`, `media/`, `backups/`, and `logs/` are runtime directories for local DB, uploads, backups, and logs.
- `scripts/` includes one-off utilities (e.g., data import, OCR helpers).

## Build, Test, and Development Commands
- `uv venv && source .venv/bin/activate && uv pip install -r requirements.txt` sets up the Python environment.
- `uvicorn app.main:app --reload` runs the API locally with auto-reload.
- `make install` installs Python dependencies via `requirements.txt`.
- `make lint` runs Ruff linting with autofix.
- `make format` formats Python code with Ruff formatter.
- `make mypy` runs static type checks on `app/`.
- `make test` runs pytest and compiles server-side i18n catalogs.
- `make coverage` generates coverage reports (HTML in `htmlcov/`).
- `make prettier` formats JS/JSON/YAML assets.

## Coding Style & Naming Conventions
- Python: 4-space indentation, line length 88, double quotes, and sorted imports via Ruff.
- Prefer `snake_case` for functions/variables, `PascalCase` for classes, and `test_*.py` for test modules.
- JavaScript formatting uses Prettier for `app/static/js/`.

## Testing Guidelines
- Test framework: pytest with pytest-cov (configured in `pyproject.toml`).
- Place new tests under `tests/` mirroring the app structure (e.g., `app/services/...` -> `tests/services/...`).
- Run full suite with `make test`; run coverage with `make coverage`.

## Commit & Pull Request Guidelines
- Commit history mixes English and Japanese messages without a strict convention. Keep messages short, imperative, and include scope or issue numbers when applicable (e.g., `Feature/75 report output (#77)`).
- PRs should include: clear description, linked issue (if any), and screenshots or GIFs for UI changes (templates/static).

## Configuration & Environment
- Core env vars are documented in `README.md` (e.g., `DATABASE_URL`, `MEDIA_DIR`, `BACKUP_DIR`, `LOG_FILE`).
- Local DB defaults to SQLite at `./data/necokeeper.db`; production may use `/mnt/data`.
