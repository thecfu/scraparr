# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Scraparr is a Prometheus exporter for the *arr suite (Sonarr, Radarr, Prowlarr, Bazarr, Readarr, Jellyseerr, Overseerr, Whisparr, Lidarr, Jellyfin, Kavita). It scrapes metrics from these services on configurable intervals and exposes them at `/metrics` for Prometheus to consume.

## Development Commands

```bash
# Install dev dependencies (requires uv)
just dev-install

# Run all checks (lint + tests)
just check

# Lint only
just lint                # uv run pylint --recursive=y src/scraparr

# Tests with coverage
just test                # uv run pytest tests/ -v --cov=scraparr --cov-report=term-missing

# Tests without coverage (faster)
just test-quick           # uv run pytest tests/ -v

# Run a single test file
uv run pytest tests/test_sonarr.py -v

# Run a single test by name
uv run pytest tests/test_sonarr.py -v -k "test_name"

# Docker dev environment (mounts src for live reload)
docker compose --file compose-dev.yaml up --build
```

## Architecture

### Config Loading Pipeline

Configuration merges two sources: YAML file (`config.yaml`) and environment variables. The pipeline in `scraparr.py` is:

1. `load_yaml_config_safe()` - loads YAML with `${VAR:-default}` env substitution
2. `parse_env_config()` - parses `SERVICE_FIELD` env vars (supports alias-based multi-instance: `SONARR_PROD_URL`)
3. `deep_merge(yaml, env)` - env overrides YAML; multi-instance uses `_aliases` marker dict
4. `coerce_config_types()` - converts strings to int/bool based on field name sets in `const.py`
5. `validate_service_config()` - checks required `url` and `api_key` fields

### Connector System

Each supported service follows a consistent pattern with three layers:

- **`connectors/<service>.py`** - `Module` class (thin wrapper, entry point). Every connector must expose a `Module` class. Loaded dynamically via `__import__` in `Connectors.load_connector()`.
- **`connectors/module.py`** - `ConnectorModule` ABC base class. Provides `get()`, `post()`, `get_root_folder()`, hash-based change detection (`validate_data`), and the `start()` lifecycle: `scrape() -> validate_data() -> clear() -> update_metrics()`.
- **`metrics/<service>.py`** - Prometheus `Gauge`/`Enum` definitions. Each metric uses `alias` as a label to support multi-instance configs.

Shared logic lives in `connectors/util.py` (status/genre/quality counting helpers, custom logger with module+alias context). Some services share API patterns: `sonarr.py` and `whisparr.py` both extend `SonarrApi`.

### Scrape Scheduler

`Connectors.scrape()` runs a threaded scheduler loop using `ThreadPoolExecutor`. Each connector instance has its own `interval` and runs independently. The loop tracks `(service, index, connector, next_run_time, future)` tuples and sleeps for the minimum time until the next due connector.

### Middleware

`middleware.py` is a WSGI middleware wrapping `prometheus_client.make_wsgi_app()`. It restricts access to `/metrics` only and optionally enforces Basic Auth or Bearer token authentication.

## Key Conventions

- All connectors are registered in `const.ACTIVE_CONNECTORS` with their default API versions in `const.API_VERSIONS`.
- Type coercion field sets (`INT_FIELDS`, `BOOL_FIELDS`) and env-parseable field names (`SERVICE_FIELDS`) live in `const.py` — update these when adding new config options.
- Metrics follow the naming pattern `<service>_<metric>` with per-path variants and `_total` suffixes for aggregate gauges.
- Python 3.12+ required. Dependencies managed via `uv` with `uv.lock`.
- Fork from the `dev` branch for contributions; `main` is the release branch.
