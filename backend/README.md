# favorite-shops - Backend

This directory contains the backend services for the favorite-shops application, built using AWS Lambda, API Gateway, and DynamoDB.

## Development Rules

### Python Package Management (`uv` and `uvx`)

This project strictly uses **`uv`** and **`uvx`** for Python package management and tool execution instead of `pip`, in order to ensure fast and consistent resolution.

#### 1. Running Standalone Tools (`uvx`)
Do not use `pip install` for developer tools. Instead, execute them on-demand via `uvx`:
- **Testing**: `uvx pytest tests/`
- **Formatter**: `uvx ruff format .` or `uvx black .`
- **Linter**: `uvx ruff check .`
- **Type Checker**: `uvx mypy .`

#### 2. Managing Dependencies (`uv pip`)
Use `uv` to install dependencies:
- **Install from requirements.txt**: `uv pip install -r requirements.txt`
- **Add a new package**: `uv pip install <package>`
- **Install for Lambda deployment**: `uv pip install -t <target_dir> ...`

> For detailed agent and development rules, please refer to the project root's `AGENT.md` and `.agents/skills/python-deps/SKILL.md`.
