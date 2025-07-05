# Indexer

run_indexer:
	uv run --project indexer --env-file .env -- indexer/main.py

lint_indexer:
	uv run --project indexer ruff check

format_indexer:
	uv run --project indexer ruff format

# API

run_api:
	uv run --project api --env-file .env -- fastapi run api/main.py

lint_api:
	uv run --project api ruff check

format_api:
	uv run --project api ruff format

# Common

lint: lint_indexer lint_api

format: format_indexer format_api
