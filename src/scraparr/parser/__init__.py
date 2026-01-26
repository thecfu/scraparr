"""Parses Scraparr configuration from environment or .env file."""

import os
from typing import Any, Optional, Dict, Mapping
from dotenv import dotenv_values

from scraparr.const import ACTIVE_CONNECTORS

# All known service field names (used to distinguish SONARR_URL from SONARR_PROD_URL)
SERVICE_FIELDS = {'url', 'api_key', 'alias', 'api_version', 'interval', 'detailed', 'within'}


def _parse_service_field(env_key: str, prefix: str) -> Optional[tuple]:
    """Parse env var to extract field name and optional alias.

    Returns (field, alias) or None if not a valid service field.
    - SONARR_URL -> ('url', None)
    - SONARR_PROD_URL -> ('url', 'prod')
    - SONARR_API_KEY -> ('api_key', None)
    - SONARR_PROD_API_KEY -> ('api_key', 'prod')
    """
    if not env_key.startswith(prefix):
        return None

    remainder = env_key[len(prefix):]  # e.g., "URL", "PROD_URL", "API_KEY"

    # Check each known field (longest first to match API_KEY before checking for _KEY suffix)
    for field in sorted(SERVICE_FIELDS, key=len, reverse=True):
        field_upper = field.upper()
        if remainder == field_upper:
            # Single instance: SONARR_URL
            return (field, None)
        if remainder.endswith(f'_{field_upper}'):
            # Multi-instance: SONARR_PROD_URL
            alias = remainder[:-len(f'_{field_upper}')]
            if alias:  # Ensure alias is not empty
                return (field, alias.lower())

    return None


def _parse_mapping(env: Mapping[str, str], mapping: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Parse env vars using a mapping of ENV_KEY -> config_key."""
    return {k: env[p] for p, k in mapping.items() if p in env} or None


def _build_config(env: Mapping[str, str]) -> Dict[str, Optional[Any]]:
    config: Dict[str, Optional[Any]] = {
        'general': _parse_mapping(env, {
            'GENERAL_PATH': 'path',
            'GENERAL_ADDRESS': 'address',
            'GENERAL_PORT': 'port',
            'GENERAL_WORKERS': 'workers',
            'GENERAL_LOG_LEVEL': 'log_level',
        }),
        'auth': _parse_mapping(env, {
            'AUTH_USERNAME': 'username',
            'AUTH_PASSWORD': 'password',
            'AUTH_TOKEN': 'token',
        }),
    }

    for service in ACTIVE_CONNECTORS:
        prefix = f'{service.upper()}_'
        single_config: Dict[str, Any] = {}
        multi_config: Dict[str, Dict[str, Any]] = {}  # alias -> fields

        for env_key in env:
            parsed = _parse_service_field(env_key, prefix)
            if parsed is None:
                continue

            field, alias = parsed
            value = env[env_key]  # Keep as string - type coercion after merge

            if alias is None:
                single_config[field] = value
            else:
                if alias not in multi_config:
                    multi_config[alias] = {}
                multi_config[alias][field] = value

        # Decide mode: multi-instance takes precedence if any alias vars exist
        if multi_config:
            config[service] = {'_aliases': multi_config}
        elif single_config:
            config[service] = single_config
        else:
            config[service] = None

    return config


def parse_dotenv_config(path: str = ".env") -> Dict[str, Optional[Any]]:
    """Parse configuration from a .env file at the given path."""
    return _build_config(dotenv_values(path))  # type: ignore


def parse_env_config() -> Dict[str, Optional[Any]]:
    """Parse configuration from the current environment variables."""
    return _build_config(os.environ)
