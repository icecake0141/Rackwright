# Rackwright

Rackwright is a Flask + SQLAlchemy + SQLite web tool for generating ZeroStage on-prem deployment artifacts (Word, Excel, image placeholder), with CSV cabling workflows, versioning, and diff outputs.

## Environment

- Python: 3.11+
- Database: SQLite
- Web: Flask (server-side rendered templates)
- ORM/Migrations: SQLAlchemy + Alembic
- Tests: pytest

## Setup

1. Create and activate virtual environment.
2. Install dependencies.

Example:

python -m venv .venv
source .venv/bin/activate
pip install -e .

## Database Setup

Initialize schema with Alembic:

alembic upgrade head

For a fresh local DB, the default URL is in alembic.ini:

sqlite:///./rackwright.db

## Run

Run Flask app (example):

python - <<'PY'
from rackwright.app import create_app
app = create_app("sqlite:///./rackwright.db")
app.run(host="127.0.0.1", port=5000, debug=False)
PY

Important:

- Use debug=False in production.
- Do not run Flask debug mode in production environments.

## Run (Next Architecture Preview)

Run the `src/`-based app with the migration launcher:

python app_next.py

Optional environment variables:

- RACKWRIGHT_DATABASE_URL (default: sqlite:///./rackwright_next.db)
- RACKWRIGHT_HOST (default: 127.0.0.1)
- RACKWRIGHT_PORT (default: 8010)
- RACKWRIGHT_DEBUG (default: 0)

## Tests

Run all tests:

python -m pytest -q

## Development Quality Gates

Install dev dependencies:

pip install -e ".[dev]"

Run formatting, linting, type checks, and tests:

pre-commit run --all-files
python -m ruff check .
python -m black --check .
python -m mypy src/rackwright rackwright tests
python -m pytest -q

## Configuration

Main runtime configuration is environment-variable based.

- RACKWRIGHT_DATA_DIR
	- Default: ./data
	- Purpose: root directory for generated artifacts and diff outputs.
	- Effective artifact path pattern:
		/projects/{project_id}/versions/{version_number}/{type}/...

If RACKWRIGHT_DATA_DIR is not set, Rackwright uses ./data.

## Data Directory and Permissions

- Generated artifacts are written under RACKWRIGHT_DATA_DIR.
- Ensure the process user has read/write permissions for this directory.
- For operations, restrict directory permissions to the service account only (least privilege).

## Security and Operational Notes

- device_vars may store plaintext in this release.
	- UI includes a warning in Device > Settings.
	- Treat DB and backup handling as sensitive operations.
- Disable debug mode in production.
- Keep secrets and deployment-specific settings in environment variables.

## Known Limitations (Current Scope)

- Word diff marking inserts highlight and comments on changed paragraphs conservatively.
- Image generation is a phase-1 placeholder SVG.
- CSV/table workflows are the primary interface for large cabling datasets.
- No authentication/authorization in this release.

## Repository Docs

- docs/spec: detailed specification
- docs/plan: implementation plan
- docs/checklists: post-implementation checklist
- docs/architecture: staged layered architecture notes
- tasks: task-by-task implementation units
