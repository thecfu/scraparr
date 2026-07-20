# Configuration

Scraparr can be configured via a **YAML file**, **environment variables**, or a combination of both. Environment variables override YAML values when both are set.

## Configuration Methods

### YAML File

Mount or place a `config.yaml` file. In Docker, mount it to `/app/src/scraparr/config/config.yaml`.

YAML supports environment variable substitution:

```yaml
sonarr:
  url: http://${SONARR_HOST:-sonarr}:8989
  api_key: ${SONARR_API_KEY}
```

| Syntax | Behavior |
|--------|----------|
| `${VAR_NAME}` | Required - fails if not set |
| `${VAR_NAME:-default}` | Optional - uses fallback if not set |

### Environment Variables

Set variables using the pattern `SERVICE_FIELD`, e.g. `SONARR_URL`, `RADARR_API_KEY`.

For Docker secrets, use the `_FILE` suffix to point to a mounted secret:

```bash
SONARR_API_KEY_FILE=/run/secrets/sonarr_api_key
```

## General Settings

Configure under `general:` in YAML or with `GENERAL_*` env vars.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `address` | string | `0.0.0.0` | Listen address |
| `port` | int | `7100` | Listen port |
| `path` | string | `/metrics` | Metrics endpoint path |
| `log_level` | string | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `workers` | int | `5` | Thread pool size for concurrent scrapes |

```yaml
general:
  port: 7100
  log_level: INFO
  workers: 5
```

## Authentication

Configure under `auth:` in YAML or with `AUTH_*` env vars. All fields are optional - if none are set, the `/metrics` endpoint is open.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `username` | string | - | HTTP Basic Auth username |
| `password` | string | - | HTTP Basic Auth password |
| `token` | string | - | Bearer token |

Basic Auth requires both `username` and `password`. Bearer token auth is independent - set `token` alone.

```yaml
auth:
  username: prometheus
  password: ${AUTH_PASSWORD}
```

## Service Configuration

Every service (connector) shares a set of common options, plus service-specific ones documented in [connectors.md](connectors.md).

### Common Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | string | **(required)** | Base URL of the service |
| `api_key` | string | **(required)** | API key for authentication |
| `alias` | string | service name | Label for Prometheus metrics to distinguish instances |
| `api_version` | string | per-service | API version path segment (see [connectors.md](connectors.md) for defaults) |
| `interval` | int | `30` | Scrape interval in seconds |
| `detailed` | bool | `false` | Enable per-item metrics (higher cardinality) |

Some connectors support additional options like `exclude`, `episode_quality_stats`, `within`, `session_details`, `client_info`, and `legacy_auth`. See [connectors.md](connectors.md) for details.

```yaml
sonarr:
  url: http://sonarr:8989
  api_key: ${SONARR_API_KEY}
  alias: sonarr-main
  interval: 60
  detailed: true
```

## Multiple Instances

### YAML - Use a List

```yaml
sonarr:
  - url: http://sonarr:8989
    api_key: key1
    alias: sonarr-main
  - url: http://sonarr2:8989
    api_key: key2
    alias: sonarr-secondary
```

> **Important:** When running multiple instances of the same service, you **must** set unique `alias` values - otherwise metrics will overwrite each other.

### Environment Variables - Alias-Based Naming

Insert an alias segment between the service name and field name:

```bash
SONARR_MAIN_URL=http://sonarr:8989
SONARR_MAIN_API_KEY=main-key

SONARR_SECONDARY_URL=http://sonarr2:8989
SONARR_SECONDARY_API_KEY=secondary-key
```

The alias (`MAIN`, `SECONDARY`) becomes the instance identifier in metrics.

## Docker Compose Example

```yaml
services:
  scraparr:
    image: ghcr.io/thecfu/scraparr
    ports:
      - "7100:7100"
    volumes:
      - ./config.yaml:/app/src/scraparr/config/config.yaml
    environment:
      - SONARR_API_KEY_FILE=/run/secrets/sonarr_api_key
    secrets:
      - sonarr_api_key

secrets:
  sonarr_api_key:
    file: ./secrets/sonarr_api_key
```

## Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: 'scraparr'
    static_configs:
      - targets: ['scraparr:7100']
```
